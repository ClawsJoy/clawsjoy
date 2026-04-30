FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt
COPY bin/requirements.txt ./bin/

# 安装依赖（在容器内，没有外部环境限制）
RUN pip install --no-cache-dir -r bin/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY bin/ ./bin/
COPY skills/ ./skills/
COPY web/ ./web/
COPY tenants/ ./tenants/
COPY data/ ./data/

RUN mkdir -p /app/logs /app/outbox

EXPOSE 8082 8088 8090 8092 8084 8085 8086 8087 8088 8089 8091

COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

CMD ["/docker-start.sh"]
