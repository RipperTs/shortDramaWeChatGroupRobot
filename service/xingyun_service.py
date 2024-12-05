from urllib.parse import quote
import requests
from lxml import etree
import time


class XingYunService:
    """
    星云短剧搜索
    """

    def __init__(self):
        self.base_url = "https://www.ssyhb.cn"

    def search_dj(self, keyword):
        """
        搜索短剧
        :param keyword:
        :return:
        """
        encoded_keyword = quote(keyword)
        url = f"https://www.ssyhb.cn/search/{encoded_keyword}.html"
        response = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}
                                , timeout=30)
        if response.status_code != 200:
            return ""

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
                        kkurl = self._search_dj_detail(link[0])
                        content += f"{i}、{drama_name} {kkurl}\n\n"
                    except Exception as e:
                        print(f"获取详情失败: {str(e)}")
                        continue
            except Exception as e:
                print(f"星云短剧获取失败: {e}")
                continue
            finally:
                time.sleep(0.5)

        return content

    def _search_dj_detail(self, url):
        """
        获取详情页面数据
        :param url:
        :return:
        """
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
                return None

            return pan_link

        except requests.exceptions.Timeout:
            return None
        except Exception as e:
            print(f"获取详情失败: {str(e)}")
            return None
