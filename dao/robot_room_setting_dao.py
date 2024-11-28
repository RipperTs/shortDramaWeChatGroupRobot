from typing import List

from database.db import db_session
from database.models import RobotRoomSettings


class RobotRoomSettingDao:
    """
    群机器人设置
    """

    @staticmethod
    def create(**kwargs) -> RobotRoomSettings:
        with db_session() as session:
            room = RobotRoomSettings(**kwargs)
            session.add(room)
            return room

    @staticmethod
    def get_by_wxid(wxid: str) -> List[RobotRoomSettings]:
        with db_session() as session:
            result = session.query(RobotRoomSettings).filter(RobotRoomSettings.admin_wxid == wxid).all()
            session.expunge_all()
            return result
