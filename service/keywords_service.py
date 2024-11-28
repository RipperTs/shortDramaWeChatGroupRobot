import logging
import queue
import threading
from collections import defaultdict

from commands import register_commands
from dto.command_dto import Command, CommandContext
from service.wxbot_service import WxbotService
from typing import Callable, Tuple, List, Optional, Dict
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
wxbot_service = WxbotService()


def timeout_handler(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result_queue = queue.Queue()

            def target():
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(("success", result))
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    result_queue.put(("error", str(e)))

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

            try:
                status, result = result_queue.get(timeout=seconds)
                if status == "error":
                    return f"命令执行出错: {result}"
                return result
            except queue.Empty:
                return "命令执行超时,请稍后重试"

        return wrapper

    return decorator


class KeywordService:
    _registry: List[Command] = []  # 将_registry移到类定义的开始处作为类变量

    def __init__(self):
        self.current_topic = None
        self._lock = threading.Lock()  # 添加锁
        self.command_queues: Dict[str, queue.Queue] = defaultdict(queue.Queue)
        self.command_processors: Dict[str, threading.Thread] = {}
        if not self._registry:
            self._register_commands()

    def _get_or_create_processor(self, room_wxid: str):
        """
        获取或微信群消息的命令处理器
        """
        if room_wxid not in self.command_processors:
            def processor():
                while True:
                    try:
                        ctx = self.command_queues[room_wxid].get()
                        self._process_command(ctx)
                    except Exception as e:
                        logger.error(f"Command processor error for room {room_wxid}: {str(e)}")
                    finally:
                        self.command_queues[room_wxid].task_done()

            thread = threading.Thread(target=processor, daemon=True)
            thread.start()
            self.command_processors[room_wxid] = thread


    @timeout_handler(60)
    def _process_command(self, ctx: CommandContext):
        """
        得到命令处理结果并通过微信发送
        :return:
        """
        # 处理消息
        response = self.process_message(ctx)
        if response:
            try:
                if "data:image/png;base64," in response:
                    wxbot_service.send_img_msg(
                        ctx.talker_wxid,
                        response.replace("data:image/png;base64,", ""),
                        ctx.sender_wxid
                    )
                else:
                    wxbot_service.send_text_msg(ctx.talker_wxid, response, ctx.sender_wxid)
            except Exception as e:
                error_msg = f"发送消息失败: {str(e)}"
                logger.error(error_msg)
                wxbot_service.send_text_msg(ctx.talker_wxid, error_msg, ctx.sender_wxid)


    def trigger_keywords(self, ctx: CommandContext):
        """
        触发关键词, 并进入队列处理命令
        :return:
        """
        try:
            room_wxid = ctx.talker_wxid
            self._get_or_create_processor(room_wxid)
            self.command_queues[room_wxid].put(ctx)
        except Exception as e:
            logger.error(f"Error queueing command for room {ctx.talker_wxid}: {str(e)}")
            wxbot_service.send_text_msg(ctx.talker_wxid, "系统繁忙,请稍后重试", ctx.sender_wxid)


    @classmethod
    def command(cls, *prefixes: str, require_content: bool = True, description: str = ""):
        """
        命令装饰器
        :param prefixes:
        :param require_content:
        :param description:
        :return:
        """

        def decorator(func: Callable):
            # 确保所有前缀都是完整的命令词
            validated_prefixes = []
            for prefix in prefixes:
                if not prefix.strip():
                    continue
                # 移除可能的空白字符
                prefix = prefix.strip()
                validated_prefixes.append(prefix)

            cmd = Command(
                prefixes=tuple(validated_prefixes),
                handler=func,
                require_content=require_content,
                description=description
            )
            cls._registry.append(cmd)
            return func

        return decorator

    @classmethod
    def match_command(cls, content: str) -> Tuple[Optional[Command], str]:
        """
        匹配命令并返回处理函数和内容

        :return:
        """
        message = content.strip()
        if not message:
            return None, ""

        for command in cls._registry:
            for prefix in command.prefixes:
                if message.startswith(prefix):
                    if not command.require_content and message == prefix:
                        return command, ""

                    content = message[len(prefix):].strip()
                    if content or not command.require_content:
                        return command, content

        return None, ""

    def _register_commands(self):
        """
        注册命令
        :return:
        """
        # 获取全部命令
        commands = register_commands()
        # 注册帮助命令
        commands.append(Command(
            prefixes=("帮助",),
            handler=self.show_help,
            require_content=False,
            description="显示所有可用命令"
        ))
        commands.append(Command(
            prefixes=("管理员指令", "管理员命令", "管理员帮助"),
            handler=self.admin_show_help,
            require_content=False,
            description="显示管理员可用的命令"
        ))
        # 扩展注册命令
        self._registry.extend(commands)

    def show_help(self, ctx: CommandContext) -> str:
        """
        显示帮助信息
        :param ctx:
        :return:
        """
        help_text = ""
        num = 1
        for cmd in self._registry:
            if cmd.hidden:
                continue

            if cmd.is_admin:
                continue

            prefixes = cmd.prefixes[0]
            desc = f" - {cmd.description}" if cmd.description else ""
            help_text += f"{num}. {prefixes}{desc}\n"
            num += 1

        return help_text

    def admin_show_help(self, ctx: CommandContext) -> str:
        """
        显示管理员帮助信息
        :param ctx:
        :return:
        """
        help_text = ""
        num = 1
        for cmd in self._registry:
            if cmd.hidden:
                continue

            if cmd.is_admin:
                prefixes = cmd.prefixes[0]
                desc = f" - {cmd.description}" if cmd.description else ""
                help_text += f"{num}. {prefixes}{desc}\n"
                num += 1

        return help_text

    def process_message(self, ctx: CommandContext) -> str:
        """
        根据得到的消息内容处理消息并返回结果
        :return:
        """
        try:
            with self._lock:
                command, content = self.match_command(ctx.content)
                if command:
                    ctx.content = content
                    return command.handler(ctx)
            return ""
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"处理命令时出错: {str(e)}"

