from config import FEISHU_APPID, FEISHU_APP_SECRET
import requests
import json
from diskcache import Cache


class FeiShuService:
    """
    飞书相关服务
    """

    def __init__(self):
        self.app_id = FEISHU_APPID
        self.app_secret = FEISHU_APP_SECRET

    def get_access_token(self):
        """
        获取飞书access_token
        :return:
        """
        cache = Cache('cache')
        access_token = cache.get('feishu_access_token')
        if access_token:
            return access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"

        payload = json.dumps({
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        access_token = response.json().get('tenant_access_token', '')
        cache.set('feishu_access_token', access_token, expire=7000)
        return access_token

    def get_spreadsheets_values(self):
        """
        获取表格数据
        :return:
        """
        spreadsheetToken = "TfDHsLUWkhFMdityYuycwKudnoh"
        range = "ae2886!A2:N200"
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/values/{range}?valueRenderOption=ToString&dateTimeRenderOption=FormattedString"

        access_token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.request("GET", url, headers=headers, data={})

        return response.json()


if __name__ == '__main__':
    feishu_service = FeiShuService()
    access_token = feishu_service.get_spreadsheets_values()
    print(access_token)
