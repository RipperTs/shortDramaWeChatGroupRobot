from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL


class OpenAIService:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.base_url = OPENAI_BASE_URL


    def get_chat_completions(self, image_url = ""):
        """
        聊天对话
        :param model:
        :param messages:
        :return:
        """
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        try:
            response = client.chat.completions.create(
                model="Qwen/Qwen2-VL-72B-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名数据分析师, 你的任务是帮助用户分析数据, 预测未来走向."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": "帮我分析图片中内容, 并根据图片中折线图的时间点和值帮我预测未来24小时趋势走向.\n请帮我努力尽最大的可能进行预测."
                            }
                        ]
                    }],
                stream=False
            )

            return response.choices[0].message.content
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    openai_service = OpenAIService()
    openai_service.get_chat_completions()
