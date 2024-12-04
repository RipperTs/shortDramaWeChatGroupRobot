from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from config import DATABASE_URL

# 创建数据库引擎，添加连接池配置
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # 连接池基础连接数
    max_overflow=30,  # 允许超出pool_size的连接数
    pool_timeout=60,  # 获取连接的超时时间
    pool_recycle=1800,  # 连接重用时间限制(30分钟)
    pool_pre_ping=True,  # 自动检测连接是否有效
    poolclass=QueuePool,
    connect_args={'init_command': "SET time_zone='+08:00'"}  # MySQL专用设置时区
)

# 创建会话工厂
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class TopicHeat(Base):
    __tablename__ = "topic_heats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(50), default='')
    heat = Column(BigInteger, default=0)
    room_wxid = Column(String(50), default='')
    created_at = Column(DateTime)


class TopicKeyword(Base):
    __tablename__ = "topic_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(50), default='')
    status = Column(Integer, default=1)
    shelf_time = Column(DateTime)
    xt_mcn = Column(String(50), default='')
    applet = Column(String(50), default='')
    theater = Column(String(50), default='')
    television = Column(String(50), default='')
    category = Column(String(100), default='')
    gf_material_link = Column(String(500), default='')
    other = Column(String(255), default='')
    synopsis = Column(String(500), default='')
    room_wxid = Column(String(50), default='')


class RobotRoom(Base):
    __tablename__ = "robot_room"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_wxid = Column(String(50), default='')
    notification_interval = Column(Integer, default=10)
    status = Column(Integer, default=1)
    topic_max_num = Column(Integer, default=50)
    expiration_time = Column(DateTime)
    below_standard = Column(Integer, default=30000)


class RobotRoomSettings(Base):
    __tablename__ = "robot_room_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_wxid = Column(String(50), default='')
    admin_wxid = Column(String(50), default='')
    status = Column(Integer, default=1)
    at_all = Column(Integer, default=0)
