import threading
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any

from dto.command_dto import CommandContext
from service.feishu_service import FeiShuService
from dao.topic_keyword_dao import TopicKeywordDao
from service.wxbot_service import WxbotService


@dataclass
class SyncResult:
    success_count: int = 0
    failed_keywords: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.failed_keywords is None:
            self.failed_keywords = []


class FeiShuCommand:
    def __init__(self):
        self.feishu_service = FeiShuService()
        self.wxbot_service = WxbotService()

    def sync_topic(self, ctx: CommandContext) -> str:
        """
        同步话题数据
        :return: str
        """

        def sync_topic_task() -> None:
            try:
                result = self._process_topic_data(ctx.talker_wxid)
                success_msg = f"同步完成, 共同步 {result.success_count} 条数据."

                if result.failed_keywords:
                    failed_msg = "\n同步失败的关键词:"
                    for fail_item in result.failed_keywords:
                        keyword = fail_item.get('keyword', '')
                        error = fail_item.get('error', '')
                        failed_msg += f"\n- {keyword}: {error}"
                    success_msg += failed_msg

                self.wxbot_service.send_text_msg(ctx.talker_wxid, success_msg, ctx.sender_wxid)
            except Exception as e:
                error_msg = f"同步失败: {str(e)}"
                print(error_msg)
                self.wxbot_service.send_text_msg(ctx.talker_wxid, error_msg, ctx.sender_wxid)

        thread = threading.Thread(target=sync_topic_task)
        thread.daemon = True
        thread.start()

        return "正在同步当天数据, 稍后为您返回结果.\n在此期间请勿重复操作."

    def _process_topic_data(self, room_wxid: str) -> SyncResult:
        result = SyncResult()

        def parse_datetime(date_str):
            """
            解析兼容不同的时间格式
            :param date_str:
            :return:
            """
            for fmt in ['%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"不支持的时间格式: {date_str}")

        try:
            table_data = self.feishu_service.get_spreadsheets_values(range="ae2886!A4:N200")
            values = table_data.get('data', {}).get('valueRange', {}).get('values', [])
            today = datetime.now().date()

            for item in values:
                try:
                    if not self._is_valid_item(item):
                        continue

                    topic_data = self._extract_topic_data(item)
                    shelf_datetime = parse_datetime(topic_data['shelf_time'])

                    if shelf_datetime.date() != today:
                        continue

                    if self._sync_single_topic(topic_data, shelf_datetime, room_wxid):
                        result.success_count += 1

                except Exception as e:
                    error_info = {
                        'keyword': _parse_keyword(item[2].strip()) if len(item) > 2 else 'unknown',
                        'error': str(e),
                        'raw_data': item
                    }
                    result.failed_keywords.append(error_info)

            # 再次尝试处理失败的数据
            for fail_item in result.failed_keywords.copy():
                try:
                    keyword = fail_item['keyword']
                    if keyword and keyword != 'unknown':
                        TopicKeywordDao.create(keyword=keyword, room_wxid=room_wxid)
                        result.success_count += 1
                        result.failed_keywords.remove(fail_item)
                except Exception as e:
                    print(f"重试处理失败数据出错: {str(e)}")

        except Exception as e:
            print(f"处理数据主流程失败: {str(e)}")

        return result

    @staticmethod
    def _is_valid_item(item: List[str]) -> bool:
        """检查数据项是否有效"""
        if len(item) < 14:
            print(f"数据不完整: {item}")
            return False
        return True

    @staticmethod
    def _extract_topic_data(item: List[str]) -> Dict[str, str]:
        """提取话题数据"""
        return {
            'keyword': _parse_keyword(item[3].strip()),  # 话题关键词
            'shelf_time': f"{item[0]} {item[1]}".replace('：', ':'), # 上架时间
            'xt_mcn': item[4] or '', # XT/MCN
            'applet': item[5] or '', # 小程序融合
            'theater': item[8] or '', # 剧场
            'television': item[9] or '', # 频道
            'category': item[10] or '', # 分类
            'other':  '',
            'gf_material_link': item[11] or '' # 链接
        }

    @staticmethod
    def _sync_single_topic(topic_data: Dict[str, str], shelf_datetime: datetime, room_wxid: str) -> bool:
        """同步单个话题数据"""
        existing_topic = TopicKeywordDao.get_by_keyword(topic_data['keyword'], room_wxid)

        if existing_topic:
            TopicKeywordDao.update_all(
                existing_topic.id,
                shelf_time=shelf_datetime,
                xt_mcn=topic_data['xt_mcn'],
                applet=topic_data['applet'],
                theater=topic_data['theater'],
                television=topic_data['television'],
                category=topic_data['category'],
                gf_material_link=topic_data['gf_material_link'],
                other=topic_data['other']
            )
        else:
            TopicKeywordDao.create_all(
                keyword=topic_data['keyword'],
                shelf_time=shelf_datetime,
                xt_mcn=topic_data['xt_mcn'],
                applet=topic_data['applet'],
                theater=topic_data['theater'],
                television=topic_data['television'],
                category=topic_data['category'],
                gf_material_link=topic_data['gf_material_link'],
                other=topic_data['other'],
                room_wxid=room_wxid
            )
        return True


def _parse_keyword(content: str) -> str:
    """
    格式化关键词
    :param content: str
    :return: str
    """
    return content.strip().replace(' ', '').replace('，', '').replace('、', '').replace('：', '').replace(':', '').replace(
        ',', '')


if __name__ == '__main__':
    feishu_command = FeiShuCommand()
    result = feishu_command.sync_topic(CommandContext(
        content="MS4wLjABAAAA8OjD6qEuLpusPdYmfELKY4iWMNCw5rjnAv6aiBjXi7U",
        talker_wxid='',
        sender_wxid=''
    ))
    print(result)

    time.sleep(60)

