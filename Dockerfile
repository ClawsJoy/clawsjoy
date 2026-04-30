FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（包括 Redis）
RUN apt-get update && apt-get install -y \
    curl \
    redis-server \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY bin/requirements.txt ./bin/
RUN pip install --no-cache-dir -r bin/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY bin/ ./bin/
COPY skills/ ./skills/
COPY web/ ./web/
COPY tenants/ ./tenants/
COPY data/ ./data/

# 创建必要目录
RUN mkdir -p /app/data /app/logs /app/outbox /var/lib/redis
RUN chmod -R 755 /app/data

# 暴露端口
EXPOSE 8082 8088 8090 8092 8084 8085 8086 8087 8088 8089 8091

# 启动脚本
COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

CMD ["/docker-start.sh"]
