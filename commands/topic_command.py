import base64
import io
import os
import threading

import numpy as np

from dao.topic_heat_dao import TopicHeatDao
from dao.topic_keyword_dao import TopicKeywordDao
from data_acquisition import getWebTopicList
from dto.command_dto import CommandContext
from matplotlib import font_manager
import matplotlib.pyplot as plt

from service.openai_service import OpenAIService
from service.wxbot_service import WxbotService

wxbot_service = WxbotService()
openai_service = OpenAIService()


class TopicCommand:
    """
    话题相关命令
    """

    def topic_detail(self, ctx: CommandContext):
        """
        返回话题详情
        :param ctx:
        :return:
        """
        topic = TopicKeywordDao.get(int(ctx.content), ctx.talker_wxid)
        if topic:
            return f"话题: 《{topic.keyword}》\n状态: {'启用' if topic.status == 1 else '禁用'}\n预计上架时间: {topic.shelf_time}\n星图MCN: {topic.xt_mcn}\n小程序融合: {topic.applet}\n剧场: {topic.theater}\n频道: {topic.television}\n分类: {topic.category}\n官方素材链接: {topic.gf_material_link}"

        return "未找到话题"

    def topic_list(self, ctx: CommandContext):
        """
        返回话题列表
        :param ctx:
        :return:
        """
        topic_list = TopicKeywordDao.get_all(ctx.talker_wxid)
        content = ""
        for topic in topic_list:
            content += f"{topic.id}、{topic.keyword}\n"

        if content == "":
            return "暂无话题"

        return content

    def topic_list_all(self, ctx: CommandContext):
        """
        返回全部话题列表
        :param ctx:
        :return:
        """
        topic_list = TopicKeywordDao.get_alls(ctx.talker_wxid)
        content = ""
        for topic in topic_list:
            status = "✅"
            if topic.status == 0:
                status = "🈲"
            content += f"{topic.id}、{topic.keyword} {status}\n"
        return content

    def enable_topic(self, ctx: CommandContext):
        """
        启用话题
        :param ctx:
        :return:
        """
        topic_id = int(ctx.content)
        topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
        if topic:
            TopicKeywordDao.update(topic_id, status=1)
            return f"已启用话题: {topic.keyword}"
        return "未找到话题"

    def disable_topic(self, ctx: CommandContext):
        """
        禁用话题
        :param ctx:
        :return:
        """
        topic_id = int(ctx.content)
        topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
        if topic:
            TopicKeywordDao.update(topic_id, status=0)
            return f"已禁用话题: {topic.keyword}"
        return "未找到话题"

    def delete_topic(self, ctx: CommandContext):
        """
        删除话题
        :param ctx:
        :return:
        """
        topic_id = int(ctx.content)
        topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
        if topic:
            result = TopicKeywordDao.delete(topic_id)
            if result:
                return f"已删除话题: {topic.keyword}"
            return f"话题: {topic.keyword} 删除失败了"

        return "未找到话题"

    def del_topic_all(self, ctx: CommandContext):
        """
        删除全部话题
        :param ctx:
        :return:
        """
        result = TopicKeywordDao.delete_all(ctx.talker_wxid)
        if result:
            return "已删除全部话题"
        return "删除全部话题失败"

    def add_topic(self, ctx: CommandContext):
        """
        添加话题
        :param ctx:
        :return:
        """
        topic = TopicKeywordDao.get_by_keyword(ctx.content, ctx.talker_wxid)
        view_count = self.search_and_create_topic(ctx.content, ctx.talker_wxid)
        if topic:
            self.enable_topic(CommandContext(
                content=str(topic.id)
            ))
            return f"已添加话题: 《{ctx.content}》\n当前热度值: {self.format_number(view_count)}"

        TopicKeywordDao.create(keyword=ctx.content, room_wxid=ctx.talker_wxid)
        return f"已添加话题: 《{ctx.content}》\n当前热度值: {self.format_number(view_count)}"

    def search_topic(self, ctx: CommandContext):
        """
        搜索抖音话题
        :param keyword:
        :return:
        """
        topic_list = getWebTopicList(ctx.content)
        content = ""
        for i, topic in enumerate(topic_list, 1):
            content += f"{i}、《{topic['cha_name']}》 {self.format_number(topic['view_count'])}\n"
        return content

    def format_number(self, num):
        """
        格式化数字
        :param num:
        :return:
        """
        if num >= 10000:
            return f"{num / 10000:.1f}w"
        elif num >= 1000:
            return f"{num / 1000:.1f}k"
        return str(num)

    def setup_chinese_font(self):
        """配置中文字体"""
        # 常见的中文字体路径
        chinese_fonts = [
            # Ubuntu 字体路径
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        ]

        # 遍历查找可用的中文字体
        font_path = None
        for font in chinese_fonts:
            if os.path.exists(font):
                font_path = font
                break

        if font_path is None:
            # 如果找不到预设字体，尝试在系统字体中查找中文字体
            fonts = font_manager.findSystemFonts()
            for font in fonts:
                try:
                    if any(name in font.lower() for name in ['wqy', 'micro', 'noto', 'chinese', 'cjk']):
                        font_path = font
                        break
                except:
                    continue

        if font_path:
            # 添加字体文件
            font_manager.fontManager.addfont(font_path)
            prop = font_manager.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = prop.get_name()
            print(f"Successfully loaded font: {font_path}")
        else:
            print("Warning: No Chinese font found. Chinese characters may not display correctly.")

        plt.rcParams['axes.unicode_minus'] = False
        return True

    def topic_trends(self, ctx: CommandContext):
        """
        话题热度趋势图
        :param ctx:
        :return:
        """
        topic_id = int(ctx.content)
        topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
        if not topic:
            return "未找到话题"

        if topic.status == 0:
            return "话题已被禁用"

        trends_data = TopicHeatDao.get_heat_diffs(topic.keyword, 250)
        if len(trends_data) == 0:
            return "暂无趋势数据"
        try:
            # 设置中文字体
            self.setup_chinese_font()

            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            # 分离时间和热度差值
            dates, diffs = zip(*trends_data)

            # 数据标准化处理
            diffs_array = np.array(diffs)
            normalized_diffs = (diffs_array - np.mean(diffs_array)) / np.std(diffs_array)

            # 创建图表，调整高度以适应说明文本
            plt.figure(figsize=(12, 8))

            # 创建子图，保留底部空间给文本
            ax = plt.subplot(111)

            # 使用半透明的填充区域增强视觉效果
            plt.fill_between(dates, normalized_diffs, alpha=0.3)
            plt.plot(dates, normalized_diffs, marker='o', markersize=2, label='热度变化')

            # 设置标题和标签
            plt.title(f"话题: {topic.keyword} - 热度趋势(标准化)", pad=20)
            plt.xlabel("时间")
            plt.ylabel("热度变化(标准化)")

            # 添加网格线增强可读性
            plt.grid(True, linestyle='--', alpha=0.7)

            # 旋转x轴日期标签，防止重叠
            plt.xticks(rotation=45)

            # 设置合适的y轴范围
            y_margin = 0.1 * (max(normalized_diffs) - min(normalized_diffs))
            plt.ylim(min(normalized_diffs) - y_margin, max(normalized_diffs) + y_margin)

            # 添加标准化说明文本
            explanation = (
                "标准化说明：\n"
                "• 0点表示平均热度水平\n"
                "• 正值表示高于平均热度（1.0表示高于平均一个标准差）\n"
                "• 负值表示低于平均热度（-1.0表示低于平均一个标准差）\n"
                "• 此标准化处理可以直观地展示热度相对变化"
            )

            # 在底部添加文本说明
            plt.figtext(0.1, 0.02, explanation, fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray',
                                  boxstyle='round,pad=0.5'),
                        wrap=True)

            # 调整布局
            plt.tight_layout()
            # 调整上下边距，为底部文本留出空间
            plt.subplots_adjust(bottom=0.25)

            # 将图表转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return "data:image/png;base64," + image_base64
        except Exception as e:
            return f"生成趋势图失败: {e}"

    def topic_prediction(self, ctx: CommandContext):
        """
        预测话题趋势
        :param ctx:
        :return:
        """
        topic_id = int(ctx.content)
        topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
        if not topic:
            return "未找到话题"

        if topic.status == 0:
            return "话题已被禁用"

        # 创建新线程来处理预测任务
        def prediction_task():
            trends_data = self.topic_trends(ctx)

            if "data:image/png;base64," not in trends_data:
                wxbot_service.send_text_msg(ctx.talker_wxid, "未找到趋势数据, 无法进行预测")
                return

            ask_content = openai_service.get_chat_completions(image_url=trends_data)
            wxbot_service.send_text_msg(ctx.talker_wxid, ask_content, ctx.sender_wxid)

        # 启动新线程
        thread = threading.Thread(target=prediction_task)
        thread.daemon = True  # 设置为守护线程,主线程结束时会一起结束
        thread.start()

        return "正在进行预测，结果稍后返回...."

    def disable_topics(self, ctx: CommandContext):
        """
        批量禁用话题
        :param ctx: content格式为逗号分隔的ID字符串，如"1,2,3"
        :return: str
        """
        topic_ids = [int(id.strip()) for id in ctx.content.split(',')]
        success_topics = []
        failed_topics = []

        for topic_id in topic_ids:
            topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
            if topic:
                TopicKeywordDao.update(topic_id, status=0)
                success_topics.append(topic.keyword)
            else:
                failed_topics.append(str(topic_id))

        result = []
        if success_topics:
            result.append(f"已禁用话题: {', '.join(success_topics)}")
        if failed_topics:
            result.append(f"未找到话题ID: {', '.join(failed_topics)}")

        return "\n".join(result) if result else "无效的话题ID列表"

    def delete_topics(self, ctx: CommandContext):
        """
        批量删除话题
        :param ctx: content格式为逗号分隔的ID字符串，如"1,2,3"
        :return: str
        """
        topic_ids = [int(id.strip()) for id in ctx.content.split(',')]
        success_topics = []
        failed_topics = []

        for topic_id in topic_ids:
            topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
            if topic:
                if TopicKeywordDao.delete(topic_id):
                    success_topics.append(topic.keyword)
                else:
                    failed_topics.append(f"{topic_id}({topic.keyword})")
            else:
                failed_topics.append(str(topic_id))

        result = []
        if success_topics:
            result.append(f"已删除话题: {', '.join(success_topics)}")
        if failed_topics:
            result.append(f"删除失败的话题ID: {', '.join(failed_topics)}")

        return "\n".join(result) if result else "无效的话题ID列表"

    def enable_topics(self, ctx: CommandContext):
        """
        批量启用话题
        :param ctx: content格式为逗号分隔的ID字符串，如"1,2,3"
        :return: str
        """
        topic_ids = [int(id.strip()) for id in ctx.content.split(',')]
        success_topics = []
        failed_topics = []

        for topic_id in topic_ids:
            topic = TopicKeywordDao.get(topic_id, ctx.talker_wxid)
            if topic:
                TopicKeywordDao.update(topic_id, status=1)
                success_topics.append(topic.keyword)
            else:
                failed_topics.append(str(topic_id))

        result = []
        if success_topics:
            result.append(f"已启用话题: {', '.join(success_topics)}")
        if failed_topics:
            result.append(f"未找到话题ID: {', '.join(failed_topics)}")

        return "\n".join(result) if result else "无效的话题ID列表"

    def search_and_create_topic(self, content, room_wxid: str):
        """
        搜索话题并创建记录
        :param content为要搜索的关键词
        :return: str
        """
        # 搜索话题
        topic_list = getWebTopicList(content)
        if not topic_list or len(topic_list) == 0:
            return False

        view_count = 0
        for topic in topic_list:
            if topic['cha_name'] == content:
                view_count = topic['view_count']
                break

        if view_count == 0:
            return False

        # 创建热度记录
        TopicHeatDao.create(
            keyword=content,
            heat=view_count,
            room_wxid=room_wxid
        )

        return view_count


if __name__ == '__main__':
    service = TopicCommand()
    print(service.del_topic_all(CommandContext(content="!")))
