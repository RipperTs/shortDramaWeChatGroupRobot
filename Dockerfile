FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 更新系统并安装依赖
RUN apt-get update && \
    apt-get install -y \
    ca-certificates \
    openssl \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    ttf-wqy-microhei \
    ttf-wqy-zenhei \
    xfonts-wqy && \
    update-ca-certificates && \
    pip install --no-cache-dir --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 暴露端口
EXPOSE 12300

# 运行应用程序
CMD ["python", "main.py"]