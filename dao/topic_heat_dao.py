from datetime import datetime
from typing import List, Tuple

from sqlalchemy import text

from database.db import db_session
from database.models import TopicHeat
from dto.topic_heat_dto import TopicNotifyResult


class TopicHeatDao:
    @staticmethod
    def create(keyword: str, heat: int, room_wxid: str):
        """
        创建话题热度
        :param keyword:
        :param heat:
        :param room_wxid:
        :return:
        """
        with db_session() as session:
            topic = TopicHeat(keyword=keyword, heat=heat, room_wxid=room_wxid, created_at=datetime.now())
            session.add(topic)
            return topic

    @staticmethod
    def get(id: int):
        with db_session() as session:
            session.expunge_all()
            return session.query(TopicHeat).get(id)

    @staticmethod
    def update(id: int, keyword: str = None, heat: int = None):
        with db_session() as session:
            topic = session.query(TopicHeat).get(id)
            if topic:
                if keyword is not None:
                    topic.keyword = keyword
                if heat is not None:
                    topic.heat = heat
            return topic

    @staticmethod
    def delete(id: int):
        with db_session() as session:
            topic = session.query(TopicHeat).get(id)
            if topic:
                session.delete(topic)
                return True
            return False

    @staticmethod
    def get_heat_diffs(room_wxid: str, keyword: str, limit: int = 50) -> List[Tuple[datetime, int]]:
        """
        获取热度差值
        :param room_wxid:
        :param keyword:
        :param limit:
        :return:
        """
        with db_session() as session:
            sql = """SELECT
                    t1.created_at,
                    COALESCE(t1.heat - t2.heat, 0) as heat_diff
                FROM (
                    SELECT *
                    FROM topic_heats
                    WHERE keyword = :keyword
                        AND heat > 0
                        AND room_wxid = :room_wxid
                    ORDER BY created_at DESC
                    LIMIT :limit
                ) t1
                LEFT JOIN topic_heats t2 ON t1.keyword = t2.keyword
                    AND t2.created_at = (
                        SELECT created_at
                        FROM topic_heats t3
                        WHERE t3.keyword = t1.keyword
                            AND t3.created_at < t1.created_at
                            AND heat > 0
                            AND room_wxid = :room_wxid
                        ORDER BY created_at DESC
                        LIMIT 1
                    )
                ORDER BY t1.created_at DESC
                """
            result = session.execute(text(sql), {'keyword': keyword, 'limit': limit})
            return [(row[0], row[1]) for row in result]

    @staticmethod
    def get_heat_notify_list(room_wxid: str) -> List[TopicNotifyResult]:
        """
        获取话题热度通知列表
        :param room_wxid:
        :return:
        """
        with db_session() as session:
            sql = """SELECT
                        tk.id,
                        tk.television,
                        tk.category,
                        th.keyword,
                        th.heat,
                        th.created_at
                    FROM topic_heats th
                    INNER JOIN topic_keywords tk ON th.keyword = tk.keyword
                    WHERE tk.status = 1
                    AND th.heat > 0
                    AND th.room_wxid = :room_wxid
                    AND (
                        SELECT COUNT(*)
                        FROM topic_heats th2
                        WHERE th2.keyword = th.keyword
                        AND th2.created_at >= th.created_at
                        AND th2.heat > 0
                        AND th.room_wxid = :room_wxid
                    ) <= 2
                    ORDER BY th.keyword, th.created_at DESC
                """
            result = session.execute(text(sql), {'room_wxid': room_wxid})
            session.expunge_all()
            return [TopicNotifyResult(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result]


if __name__ == '__main__':
    model = TopicHeatDao()
    for item in model.get_heat_notify_list('50153368810@chatroom'):
        print(item)
