from typing import List

from sqlalchemy.exc import SQLAlchemyError

from database.db import db_session
from database.models import TopicKeyword


class TopicKeywordDao:
    """
    话题详情dao
    """

    @staticmethod
    def create(keyword: str, status: int = 1, room_wxid: str = ''):
        with db_session() as session:
            topic = TopicKeyword(keyword=keyword, status=status, room_wxid=room_wxid)
            session.add(topic)
            return topic

    @staticmethod
    def create_all(**kwargs):
        with db_session() as session:
            topic = TopicKeyword(**kwargs)
            session.add(topic)
            return topic

    @staticmethod
    def get(id: int, room_wxid: str) -> TopicKeyword:
        with db_session() as session:
            topic_keyword = session.query(TopicKeyword).filter(TopicKeyword.id == id,
                                                               TopicKeyword.room_wxid == room_wxid).first()
            session.expunge_all()
            return topic_keyword

    @staticmethod
    def get_by_keyword(keyword: str, room_wxid: str) -> TopicKeyword:
        """
        根据关键词获取话题
        :param keyword:
        :param room_wxid:
        :return:
        """
        with db_session() as session:
            topics = session.query(TopicKeyword).filter(TopicKeyword.keyword == keyword,
                                                        TopicKeyword.room_wxid == room_wxid).first()
            session.expunge_all()
            return topics

    @staticmethod
    def get_all(room_wxid: str) -> List[TopicKeyword]:
        with db_session() as session:
            topics = session.query(TopicKeyword).filter(TopicKeyword.status == 1,
                                                        TopicKeyword.room_wxid == room_wxid).all()
            session.expunge_all()
            return topics

    @staticmethod
    def get_alls(room_wxid: str) -> List[TopicKeyword]:
        with db_session() as session:
            topics = session.query(TopicKeyword).filter(TopicKeyword.room_wxid == room_wxid).all()
            session.expunge_all()
            return topics

    @staticmethod
    def update(id: int, keyword: str = None, status: int = None):
        with db_session() as session:
            topic = session.query(TopicKeyword).get(id)
            if topic:
                if keyword is not None:
                    topic.keyword = keyword
                if status is not None:
                    topic.status = status
            return topic

    @staticmethod
    def update_all(id: int, **kwargs):
        with db_session() as session:
            try:
                topic = session.query(TopicKeyword).get(id)
                if topic:
                    for key, value in kwargs.items():
                        setattr(topic, key, value)
                    session.commit()  # 需要添加commit
                    return topic
                return None  # 如果找不到记录，返回None
            except Exception as e:
                session.rollback()  # 发生异常时回滚
                raise e

    @staticmethod
    def delete(id: int):
        with db_session() as session:
            topic = session.query(TopicKeyword).get(id)
            if topic:
                session.delete(topic)
                return True
            return False

    @staticmethod
    def delete_all(room_wxid: str):
        with db_session() as session:
            try:
                # 查询总数,用于返回
                total = session.query(TopicKeyword).count()
                # 执行批量删除
                session.query(TopicKeyword).filter(TopicKeyword.room_wxid == room_wxid).delete(
                    synchronize_session='fetch')
                session.commit()
                return total
            except SQLAlchemyError as e:
                session.rollback()
                raise e
