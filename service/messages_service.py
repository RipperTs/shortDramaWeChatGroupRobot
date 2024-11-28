from dao.robot_room_dao import RobotRoomDao
from dto.command_dto import CommandContext
from service.keywords_service import KeywordService
from config import MESSAGE_GROUP, SUPER_ADMIN

keyword_service = KeywordService()


class MessageService:
    """
    微信消息处理服务
    """

    def __init__(self):
        self.message_group = MESSAGE_GROUP
        self.super_admin = SUPER_ADMIN

    def get_messages(self, request_json):
        # 解析消息
        # print(request_json)
        for msg in request_json.get('data', []):
            strTalker = msg.get('StrTalker', '')
            isSender = msg.get('IsSender', 1)
            if isSender == 1:
                continue

            sender_wxid = msg.get('Sender', '')
            content = msg.get('StrContent', '')
            # 如果是启用/禁用机器人命令,跳过权限校验
            if content in ["启用机器人", "禁用机器人"]:
                ctx = CommandContext(
                    content=content,
                    talker_wxid=strTalker,
                    sender_wxid=sender_wxid,
                    bytes_extra=msg.get('BytesExtra', '')
                )
                keyword_service.trigger_keywords(ctx)
                return

            # 不是超级管理员则检查群是否被授权
            if sender_wxid not in self.super_admin:
                robot_room_result = RobotRoomDao.get_by_room_wxid(strTalker)
                if robot_room_result is None:
                     return

            ctx = CommandContext(
                content=content,
                talker_wxid=strTalker,
                sender_wxid=sender_wxid,
                bytes_extra=msg.get('BytesExtra', '')
            )
            keyword_service.trigger_keywords(ctx)
