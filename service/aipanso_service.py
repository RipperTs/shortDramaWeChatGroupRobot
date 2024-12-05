import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import requests
import re
from diskcache import Cache
from urllib.parse import quote
from lxml import html

from config import AIPANSO_CODE
from service.shenlongip_service import ShenLongIPService


class AiPanSoService:
    """
    爱盘搜数据抓取
    https://www.aipanso.com
    """

    def __init__(self):
        self.global_headers = {
            'Host': 'www.aipanso.com',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"macOS"',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'DNT': '1',
            'Origin': 'https://www.aipanso.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.aipanso.com/s/z5g0LI1Beh0oVZZsepcbsU7b',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.shelongip_service = ShenLongIPService()

    def get_egg_cookie(self, code: str):
        """
        获取身份认证后的 cookie
        :param code:
        :return:
        """
        cache = Cache('cache')
        cache_key = f"egg_account_cookie_{code}"
        cache_data = cache.get(cache_key)
        if cache_data:
            return cache_data

        url = "https://www.aipanso.com/active"
        payload = f'code={code}'

        self.global_headers['Cookie'] = ''
        # 根据参数获取 cookie 的值 (有效期 10 分钟)
        first_start_load_value = self.get_first_start_load_value("POST", url, payload)
        if first_start_load_value is None:
            return None

        cookie_value = self.start_load(first_start_load_value)
        self.global_headers['Cookie'] = cookie_value
        response = requests.request("POST", url, headers=self.global_headers, data=payload, timeout=30,
                                    proxies=self.shelongip_service.get_ip())

        # 获取响应 cookie
        cookie_value = response.cookies.get_dict().get('_egg', None)
        cache.set(cache_key, cookie_value, expire=86400 * 3)
        return cookie_value

    def get_first_start_load_value(self, method, url, payload):
        """
        第一次请求获取 start_load 参数
        :return:
        """
        response = requests.request(method, url, headers=self.global_headers, data=payload, timeout=30,
                                    proxies=self.shelongip_service.get_ip())

        print(response.text)
        pattern = r'start_load\("([^"]+)"\)'
        match = re.search(pattern, response.text)
        if match:
            return match.group(1)
        return None

    def get_pan_url(self, fid: str):
        """
        获取网盘地址
        :param fid:
        :return:
        """
        url = f"https://www.aipanso.com/cv/{fid}"
        egg_cookie = self.get_egg_cookie(AIPANSO_CODE)
        if egg_cookie is None:
            raise Exception("网站获取 cookie 失败, 无法获取网盘地址")

        cookie = f"_egg={egg_cookie};"
        self.global_headers['Cookie'] = cookie

        # 根据参数获取 cookie 的值 (有效期 10 分钟)
        first_start_load_value = self.get_first_start_load_value("GET", url, None)
        if first_start_load_value is None:
            raise Exception("网站获取参数, 无法获取网盘地址")

        cookie_value = self.start_load(first_start_load_value)
        self.global_headers['Cookie'] = cookie + cookie_value
        self.global_headers['Referer'] = url
        self.global_headers[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'

        # 获取最终网盘地址
        response = requests.request("GET", url, headers=self.global_headers, timeout=30, allow_redirects=True,
                                    proxies=self.shelongip_service.get_ip())
        redirected_url = response.url if response.history else None
        return redirected_url

    def start_load(self, input_data):
        """
        获取 cookie 加密参数
        :param input_data:
        :return:
        """
        # AES 加密配置
        encryption_key = b"1234567812345678"  # 16字节的密钥

        # 创建 AES 加密器，使用 CBC 模式
        cipher = AES.new(encryption_key, AES.MODE_CBC, iv=encryption_key)

        # 对输入数据进行填充和加密
        padded_data = pad(input_data.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)

        # 转换为十六进制
        hex_output = binascii.hexlify(encrypted).decode()

        return f"ck_ml_sea_={hex_output}"

    def get_search_result(self, keyword):
        encoded_keyword = quote(keyword)
        url = f"https://www.aipanso.com/search?k={encoded_keyword}"

        # 根据参数获取 cookie 的值 (有效期 10 分钟)
        first_start_load_value = self.get_first_start_load_value("GET", url, None)
        if first_start_load_value is None:
            raise Exception("网站获取参数, 无法获取网盘地址")

        cookie_value = self.start_load(first_start_load_value)
        self.global_headers['Cookie'] = cookie_value

        def parse_data(html_content):
            """
            解析 html
            :param html_content:
            :return:
            """
            try:
                tree = html.fromstring(html_content)

                # Get all the van-row elements containing links and titles
                rows = tree.xpath('//van-row[.//van-card]')

                results = []
                for row in rows:
                    try:
                        # Extract link
                        link = row.xpath('.//a/@href')[0]

                        # Extract full title (combining all text within the title div)
                        title = ''.join(
                            row.xpath(
                                './/div[@style="font-size:medium;font-weight: 550;padding-top: 5px;"]//text()')).strip()

                        results.append({
                            'link': link,
                            'title': title
                        })
                    except:
                        continue

                return results
            except Exception as e:
                print(f"解析数据失败: {e}")
                return []

        response = requests.request("GET", url, headers=self.global_headers, timeout=30,
                                    proxies=self.shelongip_service.get_ip())
        return parse_data(response.text)

    def search_dj(self, keyword):
        """
        搜索短剧
        :param keyword:
        :return:
        """
        self.global_headers['Cookie'] = ''
        self.global_headers['Referer'] = ''
        result_list = self.get_search_result(keyword)
        content = ""
        for i, item in enumerate(result_list, 1):
            try:
                if i > 2:
                    break
                fid = item['link'][3:]
                pan_url = self.get_pan_url(fid)
                if pan_url is None:
                    content += f"{i}、{item['title']} - https://www.aipanso.com/{item['link']}\n\n"
                else:
                    content += f"{i}、{item['title']} - {pan_url}\n\n"

            except Exception as e:
                print(f"爱搜盘数据获取失败: {e}")
            finally:
                time.sleep(1)

        return content


if __name__ == '__main__':
    ai_service = AiPanSoService()
    print(ai_service.search_dj("无声秘恋"))
