# ClawsJoy Docker 镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY bin/ ./bin/
COPY skills/ ./skills/
COPY web/ ./web/
COPY tenants/ ./tenants/
COPY data/ ./data/
COPY config/ ./config/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r bin/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建运行时目录
RUN mkdir -p /app/logs /app/outbox

# 暴露端口
EXPOSE 8082 8084 8085 8086 8087 8088 8089 8090 8091 8092

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8088/api/tenants || exit 1

# 启动脚本
COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

CMD ["/docker-start.sh"]

# 安装 Whisper STT 依赖

# 安装额外依赖
