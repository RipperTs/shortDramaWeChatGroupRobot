from datetime import datetime

from dateutil.relativedelta import relativedelta

from config import SUPER_ADMIN
from dao.robot_room_dao import RobotRoomDao
from dao.robot_room_setting_dao import RobotRoomSettingDao
from dto.command_dto import CommandContext
from scheduled.topic_task import TopicTaskScheduled
from service.wxbot_service import WxbotService
import base64
import re


class RoomCommand:
    """
    微信群管理命令
    """

    def __init__(self):
        # 超级管理员wxid
        self.super_admin = SUPER_ADMIN
        self.wxbot_service = WxbotService()

    def notify_all(self, ctx: CommandContext):
        """
        通知群所有人
        :param content:
        :return:
        """
        robot_room_setting = RobotRoomSettingDao.get_by_wxid(ctx.talker_wxid)
        if ctx.sender_wxid not in self.super_admin and ctx.sender_wxid not in [setting.admin_wxid for setting in
                                                                               robot_room_setting]:
            return "权限不足."

        self.wxbot_service.send_text_msg_to_all(ctx.talker_wxid, ctx.content)
        return ""

    def authorize_room(self, ctx: CommandContext):
        """
        授权群
        :param ctx:
        :return:
        """
        if ctx.sender_wxid not in self.super_admin:
            return "权限不足."

        robot_result = RobotRoomDao.get_by_room_wxid_igon(ctx.talker_wxid)
        if robot_result:
            return "群已授权."

        # 获取当前时间
        now = datetime.now()
        expire_time = now + relativedelta(months=12)
        result = RobotRoomDao.create(room_wxid=ctx.talker_wxid, expiration_time=expire_time)
        if not result:
            return "操作失败."

        TopicTaskScheduled.refresh_room_task(ctx.talker_wxid)
        return "授权成功."

    def update_expire_time(self, ctx: CommandContext):
        """
        设置群授权过期时间
        :param ctx:
        :return:
        """
        if ctx.sender_wxid not in self.super_admin:
            return "权限不足."

        robot_result = RobotRoomDao.get_by_room_wxid_igon(ctx.talker_wxid)
        if not robot_result:
            return "此群还未授权."

        # 获取当前时间
        now = datetime.now()
        expire_time = now + relativedelta(months=int(ctx.content))
        result = RobotRoomDao.update_expire_time(ctx.talker_wxid, expire_time)
        if not result:
            return "操作失败."

        return "设置成功."

    def setting_admin_account(self, ctx: CommandContext):
        """
        设置群管理员
        :param ctx:
        :return:
        """
        if ctx.sender_wxid not in self.super_admin:
            return "权限不足."

        robot_result = RobotRoomDao.get_by_room_wxid_igon(ctx.talker_wxid)
        if not robot_result:
            return "此群还未授权."

        # 解码 base64
        decoded_str = base64.b64decode(ctx.bytes_extra).decode('utf-8', errors='ignore')
        pattern = r'<atuserlist>(.*?)</atuserlist>'
        match = re.search(pattern, decoded_str)
        if match:
            atuserlist = match.group(1)
            RobotRoomSettingDao.create(room_wxid=ctx.talker_wxid, admin_wxid=atuserlist, at_all=1)
            return "设置成功."

        return "设置失败."

    def enable_robot(self, ctx: CommandContext):
        """
        启用机器人
        :param ctx:
        :return:
        """
        robot_room_setting = RobotRoomSettingDao.get_by_wxid(ctx.talker_wxid)
        if ctx.sender_wxid not in self.super_admin and ctx.sender_wxid not in [setting.admin_wxid for setting in
                                                                               robot_room_setting]:
            return "权限不足."

        robot_result = RobotRoomDao.get_by_room_wxid_igon(ctx.talker_wxid)
        if not robot_result:
            return "此群还未授权"

        result = RobotRoomDao.update_status(ctx.talker_wxid, 1)
        if not result:
            return "操作失败."

        TopicTaskScheduled.refresh_room_task(ctx.talker_wxid)
        return "启用成功."

    def disable_robot(self, ctx: CommandContext):
        """
        禁用机器人
        :param ctx:
        :return:
        """
        robot_room_setting = RobotRoomSettingDao.get_by_wxid(ctx.talker_wxid)
        if ctx.sender_wxid not in self.super_admin and ctx.sender_wxid not in [setting.admin_wxid for setting in
                                                                               robot_room_setting]:
            return "权限不足."

        robot_result = RobotRoomDao.get_by_room_wxid_igon(ctx.talker_wxid)
        if not robot_result:
            return "此群还未授权"

        result = RobotRoomDao.update_status(ctx.talker_wxid, 0)
        if not result:
            return "操作失败."

        TopicTaskScheduled.del_room_task(ctx.talker_wxid)
        return "禁用成功."

    def set_min_heat(self, ctx: CommandContext):
        """
        设置最小热度
        :param ctx:
        :return:
        """
        robot_room_setting = RobotRoomSettingDao.get_by_wxid(ctx.talker_wxid)
        if ctx.sender_wxid not in self.super_admin and ctx.sender_wxid not in [setting.admin_wxid for setting in
                                                                               robot_room_setting]:
            return "权限不足."

        result = RobotRoomDao.update_min_heat(ctx.talker_wxid, int(ctx.content))
        if not result:
            return "操作失败."

        return "设置成功."

    def set_sync_time(self, ctx: CommandContext):
        """
        设置同步时间
        :param ctx:
        :return:
        """
        robot_room_setting = RobotRoomSettingDao.get_by_wxid(ctx.talker_wxid)
        if ctx.sender_wxid not in self.super_admin and ctx.sender_wxid not in [setting.admin_wxid for setting in
                                                                               robot_room_setting]:
            return "权限不足."

        timed = int(ctx.content)
        if timed < 10:
            return "时间间隔不能小于10分钟"

        result = RobotRoomDao.update_sync_time(ctx.talker_wxid, timed)
        if not result:
            return "操作失败."

        TopicTaskScheduled.refresh_room_task(ctx.talker_wxid)
        return "设置成功."


if __name__ == '__main__':
    # 获取当前时间
    now = datetime.now()
    expire_time = now + relativedelta(months=5)
    print(expire_time)
