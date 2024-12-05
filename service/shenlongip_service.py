from config import SHENLONGIP_URL, IS_PROXY
import requests
from diskcache import Cache
import json


class ShenLongIPService:
    """
    神龙 http 代理 ip
    """

    def __init__(self):
        self.base_url = SHENLONGIP_URL

    def get_ip(self):
        """
        获取代理ip
        :return:
        """
        if int(IS_PROXY) == 0:
            return None

        cache = Cache('cache')
        cache_key = "proxy_ip"
        cache_data = cache.get(cache_key)
        if cache_data:
            response_json = json.loads(cache_data)
            return self._parse_proxies(response_json)

        # 请求获取新的代理ip
        response = requests.get(self.base_url, timeout=10)
        if response.status_code != 200:
            return None

        response_json = response.json()
        if response_json.get('code', 0) != 200:
            return None

        cache.set(cache_key, response.text, expire=120)
        return self._parse_proxies(response_json)

    def _parse_proxies(self, response_json):
        """
        解析代理ip
        :param response_json:
        :return:
        """
        proxyMeta = "http://%(host)s:%(port)s" % {
            "host": response_json.get('data', [])[0]['ip'],
            "port": response_json.get('data', [])[0]['port'],
        }

        return {
            "http": proxyMeta,
            "https": proxyMeta
        }


    def refresh_ip(self):
        """
        刷新一个新的代理 ip
        :return:
        """
        cache = Cache('cache')
        cache_key = "proxy_ip"
        cache.delete(cache_key)
        return self.get_ip()


if __name__ == '__main__':
    service = ShenLongIPService()
    print(service.get_ip())
