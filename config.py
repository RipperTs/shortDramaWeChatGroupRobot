import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 数据库配置
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')

# 消息组配置
MESSAGE_GROUP = os.getenv('MESSAGE_GROUP', '').split(',')

# TikHub API Token
TIKHUB_API_TOKEN = os.getenv('TIKHUB_API_TOKEN')

# 微信机器人地址
WXBOT_URL = os.getenv('WXBOT_URL')

FEISHU_APPID = os.getenv('FEISHU_APPID')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')

# 超级管理员wxid
SUPER_ADMIN = os.getenv('SUPER_ADMIN').split(',')

DY_TOPIC_URL = os.getenv('DY_TOPIC_URL', 'https://creator.douyin.com')
AIPANSO_CODE = os.getenv('AIPANSO_CODE', '3456')

SHENLONGIP_URL = os.getenv('SHENLONGIP_URL', '')
