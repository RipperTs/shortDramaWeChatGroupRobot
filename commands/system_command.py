import time
import requests
import re
from urllib.parse import quote
from lxml import etree

from dto.command_dto import CommandContext
from config import TIKHUB_API_TOKEN


class SystemCommand:
    """
    系统级别命令
    """

    def video_parse(self, ctx: CommandContext):
        """
        视频解析
        :param ctx:
        :return:
        """
        video_url = ctx.content

        def extract_douyin_url_regex(text: str) -> str:
            # 匹配以https://开头，到空格或结束的内容
            pattern = r'https://[^\s]+'
            match = re.search(pattern, text)
            if match:
                return match.group(0)
            return ""

        def extract_douyin_vid(url: str) -> str:
            # 如果 URL 包含 "vid=" 参数
            if "vid=" in url:
                return url.split("vid=")[1].split("&")[0]
            # 如果包含 video/ 格式 (支持 douyin.com 和 iesdouyin.com)
            elif "/video/" in url:
                # 提取 video/ 后的数字部分，直到下一个 / 或 ? 或字符串结束
                vid = url.split("/video/")[1].split("/")[0].split("?")[0]
                return vid
            return ""

        try:
            url = extract_douyin_url_regex(video_url)
            if 'v.douyin.com' in url:
                response = requests.get(url, allow_redirects=False)
                url = response.headers['Location']  # 获取跳转地址
            vid = extract_douyin_vid(url)
            request_url = f"https://api.tikhub.io/api/v1/douyin/web/fetch_one_video_v2?aweme_id={vid}"
            response = requests.get(request_url, headers={
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Authorization': f'Bearer {TIKHUB_API_TOKEN}'
            }, timeout=30)

            if response.json().get('code', 0) != 200:
                print(f"请求失败：{response.text}")
                return []

            aweme_details = response.json().get('data', {}).get('aweme_details', [])
            if len(aweme_details) == 0:
                return "视频请求失败"

            url_list = aweme_details[0].get('video', {}).get('play_addr', {}).get('url_list', [])
            return url_list[len(url_list) - 1]
        except:
            return "视频处理失败"

    def search_dj(self, ctx: CommandContext):
        """
        搜索短剧
        :param ctx:
        :return:
        """
        encoded_keyword = quote(ctx.content)
        url = f"https://www.ssyhb.cn/search/{encoded_keyword}.html"
        response = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
                                , timeout=30)
        if response.status_code != 200:
            return "目标站点访问失败"

        html = etree.HTML(response.text)
        liNodes = html.xpath("//ul[@class='list']/li")

        content = ""
        for i, item in enumerate(liNodes, 1):
            if i > 5:
                break
            try:
                # 获取每个li下的剧名
                texts = item.xpath('.//a//text()')
                text = ''.join(texts).replace('\r\n', '').strip()
                drama_name = text.replace('免费在��观看', '')
                # 获取每个li下的链接
                link = item.xpath('.//h2/a/@href')
                if drama_name and link:  # 确保非空再输出
                    try:
                        kkurl = self.search_dj_detail(link[0])
                        content += f"{i}、{drama_name} {kkurl}\n\n"
                    except Exception as e:
                        content += f"{i}、获取详情失败: {str(e)}\n\n"
            except Exception as e:
                content += f"{i}、获取失败: {e}\n\n"
                continue
            finally:
                time.sleep(0.5)

        if content == "":
            return "未找到相关短剧"
        return content

    def search_dj_detail(self, url):
        try:
            response = requests.get(url, headers={
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }, timeout=30)

            if response.status_code != 200:
                return "目标站点访问失败"

            html = etree.HTML(response.text)

            # 尝试多个可能的xpath表达式
            pan_link = None
            xpath_patterns = [
                '//p/strong//a/@href',
                '//a[contains(text(), "点击领取")]/@href',
                '//div[contains(@class, "content")]//a[contains(text(), "点击领取")]/@href',
                '//div[@class="article-content"]//a/@href'
            ]

            for pattern in xpath_patterns:
                links = html.xpath(pattern)
                if links:
                    pan_link = links[0]
                    break

            if not pan_link:
                return "未找到网盘链接"

            return pan_link

        except requests.exceptions.Timeout:
            return "请求超时"
        except Exception as e:
            return f"获取详情失败: {str(e)}"

    def dy_report(self, ctx: CommandContext):
        """
        抖音自动举报作品
        :param ctx:
        :return:
        """
        request_url = f"https://api.tikhub.io/api/v1/douyin/app/v1/fetch_user_post_videos?sec_user_id={ctx.content}"
        response = requests.get(request_url, headers={
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Authorization': f'Bearer {TIKHUB_API_TOKEN}'
        }, timeout=30)

        if response.json().get('code', 0) != 200:
            print(f"请求失败：{response.text}")
            return []

        aweme_list = response.json().get('data', {}).get('aweme_list', [])

        content = ""
        for item in aweme_list:
            desc = item.get('desc', '')[:30] + '...'
            aweme_id = item.get('aweme_id', '')
            digg_count = item.get('statistics', {}).get('digg_count', 0)
            content += f"作品ID: {aweme_id}, 点赞数: {digg_count}, 描述: {desc}\n\n"

        content += f"共找到{len(aweme_list)}条作品，正在举报中，请稍后"
        return content


if __name__ == '__main__':
    service = SystemCommand()
    print(service.dy_report(CommandContext(
        content="MS4wLjABAAAA8OjD6qEuLpusPdYmfELKY4iWMNCw5rjnAv6aiBjXi7U",
        talker_wxid='',
        sender_wxid=''
    )))
