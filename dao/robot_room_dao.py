from datetime import datetime
from typing import List

from database.db import db_session
from database.models import RobotRoom


class RobotRoomDao:
    """
    群机器人
    """

    @staticmethod
    def create(**kwargs) -> RobotRoom:
        with db_session() as session:
            room = RobotRoom(**kwargs)
            session.add(room)
            return room

    @staticmethod
    def get_one(id: int) -> RobotRoom:
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.id == id).first()
            session.expunge_all()
            return result

    @staticmethod
    def get_by_room_wxid(room_wxid: str) -> RobotRoom:
        """
        获取有效的微信群机器人
        :param room_wxid:
        :return:
        """
        # 获取当前时间
        now = datetime.now()
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == room_wxid,
                                                     RobotRoom.expiration_time > now,
                                                     RobotRoom.status == 1).first()
            session.expunge_all()
            return result

    @staticmethod
    def get_room_list() -> List[RobotRoom]:
        now = datetime.now()
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.expiration_time > now,
                                                     RobotRoom.status == 1).all()
            session.expunge_all()
            return result

    @staticmethod
    def get_by_room_wxid_igon(room_wxid: str) -> RobotRoom:
        """
        获取有效的微信群机器人
        :param room_wxid:
        :return:
        """
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == room_wxid).first()
            session.expunge_all()
            return result

    @staticmethod
    def delete_by_wxid(wxid: str) -> int:
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == wxid).delete()
            return result

    @staticmethod
    def update_expire_time(wxid: str, expire_time: datetime) -> RobotRoom:
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == wxid).first()
            if result:
                result.expiration_time = expire_time
            return result

    @staticmethod
    def update_status(wxid: str, status: int) -> RobotRoom:
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == wxid).first()
            if result:
                result.status = status
            return result

    @staticmethod
    def update_min_heat(wxid: str, min_heat: int) -> RobotRoom:
        """
        更新最低热度
        :param wxid:
        :param min_heat:
        :return:
        """
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == wxid).first()
            if result:
                result.below_standard = min_heat
            return result

    @staticmethod
    def update_sync_time(wxid: str, timed: int) -> RobotRoom:
        """
        更新同步间隔时间
        :param wxid:
        :param timed:
        :return:
        """
        with db_session() as session:
            result = session.query(RobotRoom).filter(RobotRoom.room_wxid == wxid).first()
            if result:
                result.notification_interval = timed
            return result


if __name__ == '__main__':
    print(RobotRoomDao.get_by_room_wxid('52964830236@chatroom'))
