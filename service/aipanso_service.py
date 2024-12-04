from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import requests
import re
from diskcache import Cache

from config import AIPANSO_CODE


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

        # 根据参数获取 cookie 的值 (有效期 10 分钟)
        first_start_load_value = self.get_first_start_load_value("POST", url, payload)
        if first_start_load_value is None:
            return None

        cookie_value = self.start_load(first_start_load_value)
        self.global_headers['Cookie'] = cookie_value
        response = requests.request("POST", url, headers=self.global_headers, data=payload, timeout=30)
        # 获取响应 cookie
        cookie_value = response.cookies.get_dict().get('_egg', None)
        cache.set(cache_key, cookie_value, expire=86400 * 3)
        return cookie_value

    def get_first_start_load_value(self, method, url, payload):
        """
        第一次请求获取 start_load 参数
        :return:
        """
        response = requests.request(method, url, headers=self.global_headers, data=payload, timeout=30)
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

        # 获取最终网盘地址
        response = requests.request("GET", url, headers=self.global_headers, timeout=30, allow_redirects=True)
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


if __name__ == '__main__':
    ai_service = AiPanSoService()
    print(ai_service.get_pan_url("z5g0LI1Beh0oVZZsepcbsU7b"))
