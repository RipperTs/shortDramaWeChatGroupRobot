import time
import requests
import re
from urllib.parse import quote
from lxml import etree

from dto.command_dto import CommandContext
from service.aipanso_service import AiPanSoService


class SystemCommand:
    """
    系统级别命令
    """

    def __init__(self):
        self.aipanso_service = AiPanSoService()

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

        try:
            url = extract_douyin_url_regex(video_url)
            response = requests.get(f'https://videoapi.funjs.top/api/parseUrl/query?url={url}&platform=utools',
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) uTools/5.2.1 Chrome/108.0.5359.215 Electron/22.3.27 Safari/537.36'
                                    })
            if response.status_code != 200:
                return "视频解析失败."

            downurl = response.json().get('data', {}).get('downurl', '视频解析失败')
            return downurl
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
            # 接入爱盘搜数据源
            content = self.aipanso_service.search_dj(ctx.content)
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


if __name__ == '__main__':
    service = SystemCommand()
    print(service.search_dj(CommandContext(
        content="无声秘恋",
        talker_wxid='',
        sender_wxid=''
    )))
