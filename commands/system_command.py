import threading
import requests
import re

from dto.command_dto import CommandContext
from service.aipanso_service import AiPanSoService
from service.wxbot_service import WxbotService
from service.xingyun_service import XingYunService
import time


class SystemCommand:
    """
    系统级别命令
    """

    def __init__(self):
        self.aipanso_service = AiPanSoService()
        self.xingyun_service = XingYunService()
        self.wxbot_service = WxbotService()

    def video_parse(self, ctx: CommandContext):
        """
        视频解析
        :param ctx:
        :return:
        """
        video_url = ctx.content

        def extract_douyin_url_regex(text: str) -> str:
            # 匹配以https://开头，到空格或结束的内容
            pattern = r'https://[^\s]+'
            match = re.search(pattern, text)
            if match:
                return match.group(0)
            return ""

        try:
            url = extract_douyin_url_regex(video_url)
            response = requests.get(f'https://videoapi.funjs.top/api/parseUrl/query?url={url}&platform=utools',
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) uTools/5.2.1 Chrome/108.0.5359.215 Electron/22.3.27 Safari/537.36'
                                    })
            if response.status_code != 200:
                return "视频解析失败."

            downurl = response.json().get('data', {}).get('downurl', '视频解析失败')
            return downurl
        except:
            return "视频处理失败"

    def search_dj(self, ctx: CommandContext):
        """
        搜索短剧
        :param ctx:
        :return:
        """

        def do_search_handler() -> None:
            try:
                content = self.xingyun_service.search_dj(ctx.content)
                if content == "" or content is None:
                    content = self.aipanso_service.search_dj(ctx.content)

                if content == "" or content is None:
                    content = "未搜索到相关短剧."

                # 发送消息
                self.wxbot_service.send_text_msg(ctx.talker_wxid, content, ctx.sender_wxid)
            except Exception as e:
                self.wxbot_service.send_text_msg(ctx.talker_wxid, f"搜索短剧出现错误: \n{e}\n\nPS: 这可能是网络问题造成的, 你可以几分钟后重新尝试~", ctx.sender_wxid)

        thread = threading.Thread(target=do_search_handler)
        thread.daemon = True
        thread.start()

        return "正在搜索短剧, 请稍后...\n在此期间请勿搜索相同短剧."


if __name__ == '__main__':
    service = SystemCommand()
    print(service.search_dj(CommandContext(
        content="无声秘恋",
        talker_wxid='52964830236@chatroom',
        sender_wxid='F1061166944'
    )))

    time.sleep(20)
