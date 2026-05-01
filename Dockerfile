FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装系统依赖（合并层）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖（利用缓存）
COPY bin/requirements.txt ./bin/
RUN pip install --no-cache-dir -r bin/requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY bin/ ./bin/
COPY skills/ ./skills/
COPY web/ ./web/

# 创建运行时目录
RUN mkdir -p /app/logs /app/outbox

# 暴露必要端口（减少暴露）
EXPOSE 8082 8084 8087

# 复制启动脚本
COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

# 使用非 root 用户运行（安全）
RUN useradd -m -u 1000 clawsjoy && chown -R clawsjoy:clawsjoy /app
USER clawsjoy

CMD ["/docker-start.sh"]
