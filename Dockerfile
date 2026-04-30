FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY bin/requirements.txt ./bin/

# 使用阿里云镜像源
RUN pip install --no-cache-dir -r bin/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

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
