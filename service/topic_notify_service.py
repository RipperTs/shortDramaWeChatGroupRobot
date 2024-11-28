from typing import List, Dict

from dao.topic_heat_dao import TopicHeatDao
from dto.topic_heat_dto import TopicNotifyResult, HeatData


class TopicNotifyService:
    """
    话题心跳通知内容处理
    """

    @staticmethod
    def format_number(number: int) -> str:
        if number >= 10000:
            return f"{round(number / 10000, 1)}w"
        elif number >= 1000:
            return f"{round(number / 1000, 1)}k"
        return str(number)

    @staticmethod
    def process_heat_data(results: List[TopicNotifyResult], min_heat: int = 30000) -> str:
        # 整理数据
        heat_diffs: Dict[str, HeatData] = {}
        temp: Dict[str, List[TopicNotifyResult]] = {}

        # 按关键字分组
        for row in results:
            keyword = row.keyword
            if keyword not in temp:
                temp[keyword] = []
            temp[keyword].append(row)

        # 计算每个关键字的热度差值
        for keyword, records in temp.items():
            if len(records) == 2:
                diff = records[0].heat - records[1].heat
                heat_diffs[keyword] = HeatData(
                    current_heat=records[0].heat,
                    previous_heat=records[1].heat,
                    diff=diff,
                    current_time=records[0].created_at,
                    previous_time=records[1].created_at,
                    id=records[0].id,
                    television=records[0].television,
                    category=records[0].category
                )
            else:
                heat_diffs[keyword] = HeatData(
                    current_heat=records[0].heat,
                    previous_heat=0,
                    diff=0,
                    current_time=records[0].created_at,
                    previous_time=None,
                    id=records[0].id,
                    television=records[0].television,
                    category=records[0].category
                )

        # 创建三个列表来存储不同类别的数据
        high_priority = []  # diff >= 500000
        medium_priority = []  # 300000 <= diff < 500000
        low_priority = []  # 30000 <= diff < 300000
        below_standard = 0  # diff < 30000

        def format_heat_info(keyword: str, data: HeatData) -> str:
            if data.category:
                result = f"{data.id}、《{keyword}》- ({data.category})\n"
            else:
                result = f"{data.id}、《{keyword}》\n"

            result += f"当前: {TopicNotifyService.format_number(data.current_heat)} (时间: {data.current_time.strftime('%H:%M')})\n"

            if data.previous_time:
                previous_time_str = f" (时间: {data.previous_time.strftime('%H:%M')})"
            else:
                previous_time_str = " (无记录)"

            result += f"上次: {TopicNotifyService.format_number(data.previous_heat)}{previous_time_str}\n"
            result += f"差值: {TopicNotifyService.format_number(data.diff)}\n"
            result += "------------------------\n"
            return result

        # 按照热度差值进行分类
        for keyword, data in heat_diffs.items():
            if data.diff >= min_heat:
                if data.diff >= 500000:
                    high_priority.append((keyword, data))
                elif data.diff >= 300000:
                    medium_priority.append((keyword, data))
                else:
                    low_priority.append((keyword, data))
            else:
                below_standard += 1

        # 对各个类别按照diff降序排序
        high_priority.sort(key=lambda x: x[1].diff, reverse=True)
        medium_priority.sort(key=lambda x: x[1].diff, reverse=True)
        low_priority.sort(key=lambda x: x[1].diff, reverse=True)

        # 生成排序后的内容
        sections = []

        if high_priority:
            high_section = "********【重点推荐】********\n"
            for keyword, data in high_priority:
                high_section += format_heat_info(keyword, data)
            sections.append(high_section)

        if medium_priority:
            medium_section = "********【一般推荐】********\n"
            for keyword, data in medium_priority:
                medium_section += format_heat_info(keyword, data)
            sections.append(medium_section)

        if low_priority:
            low_section = "********【其他】********\n"
            for keyword, data in low_priority:
                low_section += format_heat_info(keyword, data)
            sections.append(low_section)

        # 组装最终结果
        total = f"共计 {len(heat_diffs)} 个话题, 其中 {below_standard} 个未超过{TopicNotifyService.format_number(min_heat)}.\n\n"
        total += "\n".join(sections)
        total += "\n"

        return total


if __name__ == '__main__':
    results = TopicHeatDao.get_heat_notify_list('52964830236@chatroom')
    res = TopicNotifyService.process_heat_data(results)
    print(res)
