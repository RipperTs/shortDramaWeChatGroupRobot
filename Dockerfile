FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 更新证书
RUN apt-get update && \
    apt-get install -y ca-certificates openssl && \
    update-ca-certificates

# 设置环境变量
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# 升级pip到最新版本
RUN pip install --no-cache-dir --upgrade pip

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码到镜像中
COPY . .

# 暴露端口
EXPOSE 12300

# 设置环境变量
ENV OPENAI_BASE_URL="https://api.siliconflow.cn/v1"
# 数据库配置
ENV DB_USER='your_database_user'
ENV DB_PASSWORD='your_database_password'
ENV DB_HOST='your_database_host'
ENV DB_NAME='your_database_name'

# OpenAI API Key
ENV OPENAI_API_KEY='your_openai_api_key'
ENV OPENAI_BASE_URL='your_openai_base_url'

# 开启接受消息的群或指定人的wxid
ENV MESSAGE_GROUP='wxid1,wxid2@chatroom'

# 超级管理员 wxid
ENV SUPER_ADMIN='wxid1,wxid2'

# TikHub API Token
ENV TIKHUB_API_TOKEN='your_tikhub_api_token'

# 微信机器人地址
ENV WXBOT_URL='http://127.0.0.1:8080'

ENV FEISHU_APPID=''
ENV FEISHU_APP_SECRET=''

# 运行应用程序
CMD ["python", "main.py"]