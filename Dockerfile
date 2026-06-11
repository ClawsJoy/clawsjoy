FROM python:3.10-slim

LABEL maintainer="ClawsJoy Team"
LABEL description="ClawsJoy AI Assistant - Enterprise Chatbot System"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p logs data/memories data/vector_kb

# 暴露端口
EXPOSE 5002 5012

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# 启动命令
CMD ["./start_clawsjoy.sh"]
