FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 环境变量（可选，也可以用 docker run 时传）
ENV BOT_TOKEN=8257364097:AAH4fNwUcD9B3ptvMGmKDOVgueyiJHZAHYo
ENV CHANNEL_ID=@trojan100
ENV ALLOWED_IDS=6445682540

# 启动脚本
CMD ["python3", "main.py"]
