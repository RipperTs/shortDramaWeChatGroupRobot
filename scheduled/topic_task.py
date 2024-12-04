from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from dao.robot_room_dao import RobotRoomDao
import logging

from data_acquisition import saveTopicHeat

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置执行器
executors = {
    'default': ThreadPoolExecutor(20),  # 线程池，最大20个线程
    'processpool': ProcessPoolExecutor(5)  # 进程池，最大5个进程
}

# 配置任务调度器
job_defaults = {
    'coalesce': False,  # 错过的任务会不会被补充执行
    'max_instances': 3,  # 同一个任务同时最多有3个实例在运行
    'misfire_grace_time': 300  # 任务超时容忍时间（秒）
}

# 创建调度器
scheduler = BackgroundScheduler(
    executors=executors,
    job_defaults=job_defaults,
    timezone='Asia/Shanghai'
)
scheduler.start()


# 任务执行装饰器，用于处理任务执行状态和异常
def task_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        room_wxid = args[0] if args else "unknown"

        try:
            logger.info(f"开始执行群 {room_wxid} 的任务")
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"群 {room_wxid} 的任务执行完成，耗时: {execution_time}秒")
            return result
        except Exception as e:
            logger.error(f"群 {room_wxid} 的任务执行失败: {str(e)}")
            raise

    return wrapper


class TopicTaskScheduled:

    @staticmethod
    def init_tasks():
        try:
            # 获取所有启用的群
            robot_room_list = RobotRoomDao.get_room_list()

            # 清除所有现有任务
            scheduler.remove_all_jobs()

            # 为每个群添加定时任务
            for room in robot_room_list:
                scheduler.add_job(
                    func=TopicTaskScheduled.room_task,
                    trigger='interval',
                    minutes=room.notification_interval,
                    id=f"room_{room.room_wxid}",
                    args=[room.room_wxid]
                )
                logger.info(f"已添加群 {room.room_wxid} 的定时任务，间隔 {room.notification_interval} 分钟")
        except Exception as e:
            logger.error(f"topic init tasks error: {e}")

    @staticmethod
    @task_decorator
    def room_task(room_wxid):
        """
        执行任务逻辑
        :param room_wxid:
        :return:
        """

        def is_between_midnight_and_six():
            """
            判断当前时间是否在凌晨0点到7点之间
            :return:
            """
            current_hour = datetime.now().hour
            return 0 <= current_hour < 7

        if is_between_midnight_and_six():
            return

        room_info = RobotRoomDao.get_by_room_wxid(room_wxid)
        if not room_info:
            return False

        saveTopicHeat(room_wxid)

    @staticmethod
    def refresh_room_task(room_wxid):
        """
        刷新任务逻辑
        :param room_wxid:
        :return:
        """
        try:
            room_info = RobotRoomDao.get_by_room_wxid_igon(room_wxid)
            if not room_info:
                return False

            # 删除现有任务
            job_id = f"room_{room_wxid}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

            # 如果群处于启用状态，添加新任务
            if room_info.status == 1:
                scheduler.add_job(
                    func=TopicTaskScheduled.room_task,
                    trigger='interval',
                    minutes=room_info.notification_interval,
                    id=job_id,
                    args=[room_info.room_wxid]
                )
            return True
        except Exception as e:
            logger.error(f"刷新任务失败: {e}")
            return False


    @staticmethod
    def del_room_task(room_wxid):
        """
        删除现有任务
        :param room_wxid:
        :return:
        """
        job_id = f"room_{room_wxid}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        return True
