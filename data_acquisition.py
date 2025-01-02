import json

import requests
from urllib.parse import quote
import time

from config import DY_TOPIC_URL
from dao.robot_room_dao import RobotRoomDao
from dao.topic_heat_dao import TopicHeatDao
from dao.topic_keyword_dao import TopicKeywordDao
from service.topic_notify_service import TopicNotifyService
from service.wxbot_service import WxbotService
from diskcache import Cache

"""
抖音话题数据采集入库
"""

wxbot_service = WxbotService()


def getWebTopicList(keyword):
    cache = Cache('cache')
    cache_key = f"topic_list_{keyword}"
    cache_data = cache.get(cache_key)
    if cache_data:
        return json.loads(cache_data)

    encoded_keyword = quote(keyword)
    url = f"{DY_TOPIC_URL}/aweme/v1/search/challengesug/?source=challenge_create&aid=2906&keyword={encoded_keyword}"
    response = requests.get(url, headers={
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }, timeout=30)

    try:
        result_json = json.loads(response.text)
        result = result_json.get('sug_list', [])
        cache.set(cache_key, json.dumps(result), expire=120)
        return result
    except:
        print(f"请求失败：{response.text}")
        return []


def saveTopicHeat(room_wxid: str):
    """
    保存话题热度数据
    :param room_wxid:
    :return:
    """
    topic = TopicKeywordDao.get_all(room_wxid)
    if len(topic) == 0:
        return None

    for item in topic:
        # 话题数据入库
        cache = Cache('cache')
        cache_key = f"topic_list_{item.keyword}"
        cache_data = cache.get(cache_key)
        if cache_data:
            continue
        # 抓取话题数据
        topic_list = getWebTopicList(item.keyword)
        # 解析话题热度
        view_count = parse_view_count(item.keyword, topic_list)
        TopicHeatDao.create(item.keyword, view_count, room_wxid)
        time.sleep(5)

    # 查询要通知的热度数据
    heat_notify_list = TopicHeatDao.get_heat_notify_list(room_wxid)
    # 查询机器人群信息
    robot_room_info = RobotRoomDao.get_by_room_wxid_igon(room_wxid)
    # 生成通知内容
    notify_content = TopicNotifyService.process_heat_data(heat_notify_list, robot_room_info.below_standard)
    # 发送消息到群
    wxbot_service.send_text_msg(room_wxid, notify_content)
    return True


def parse_view_count(keyword, topic_list):
    """
    解析话题列表中的播放量
    :param topic_list:
    :return:
    """
    if len(topic_list) == 0:
        return 0

    try:
        for topic in topic_list:
            if topic['cha_name'] == keyword:
                return topic['view_count']

        return 0
    except:
        return 0


if __name__ == '__main__':
    saveTopicHeat('52964830236@chatroom')
