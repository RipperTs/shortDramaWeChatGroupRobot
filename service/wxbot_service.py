import json
import requests

from config import WXBOT_URL


class WxbotService:
    """
    微信机器人服务
    """

    def __init__(self):
        self.url = WXBOT_URL


    def send_text_msg(self, wxid, content, SenderWxid=''):
        """
        发送文本消息
        :param wxid:
        :param content:
        :return:
        """
        if wxid == 'wxid_roq6lkoc17wp22' or SenderWxid == 'wxid_roq6lkoc17wp22':
            content += '\n\n(Mxh你挣不到钱的，别再问了)'

        if SenderWxid == '':
            payload = json.dumps({
                "wxid": wxid,
                "content": content
            })
        else:
            content = f"@{self.get_nickname(SenderWxid)} \n{content}"
            payload = json.dumps({
                "wxid": wxid,
                "content": content,
                "atlist": [SenderWxid]
            })

        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", f"{self.url}/api/sendtxtmsg", headers=headers, data=payload, timeout=30)
        print(response.text)


    def send_text_msg_to_all(self, wxid, content):
        """
        发送文本消息给所有人
        :param wxid:
        :param content:
        :return:
        """
        content = f"@所有人 \n{content}"
        payload = json.dumps({
            "wxid": wxid,
            "content": content,
            "atlist": ['notify@all']
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", f"{self.url}/api/sendtxtmsg", headers=headers, data=payload, timeout=30)
        print(response.text)


    def send_img_msg(self, wxid, base64image, SenderWxid=''):
        """
        发送图片消息
        :param wxid:
        :param base64image:
        :return:
        """

        if SenderWxid != '':
            self.send_text_msg(wxid, "您要的图片来了~", SenderWxid)

        payload = json.dumps({
            "wxid": wxid,
            "image": base64image
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", f"{self.url}/api/sendimgmsg", headers=headers, data=payload, timeout=30)
        print(response.text)



    def get_nickname(self, wxid):
        """
        获取微信昵称, 通过本地数据库反查方式实现
        :param wxid:
        :return:
        """
        payload = json.dumps({
            "wxid": wxid,
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", f"{self.url}/api/dbaccountbywxid", headers=headers, data=payload,
                                    timeout=15)
        return response.json().get('data', '').get('NickName', 'xxx')


if __name__ == '__main__':
    wxbot_service = WxbotService()
    print(wxbot_service.get_nickname('F1061166944'))
