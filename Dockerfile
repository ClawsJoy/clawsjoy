FROM python:3.11-slim

LABEL name="ClawsJoy"
LABEL version="5.0.0"
LABEL description="智能体矩阵系统"

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 安装Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install flask flask-cors pyyaml requests psutil pydantic tiktoken chromadb

# 复制项目
COPY . .

# 创建数据目录
RUN mkdir -p data logs

# 启动脚本
RUN echo '#!/bin/bash\nollama serve &\nsleep 2\npython3 agent_gateway_enhanced.py' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

EXPOSE 5002

ENV PYTHONUNBUFFERED=1

CMD ["/app/entrypoint.sh"]
