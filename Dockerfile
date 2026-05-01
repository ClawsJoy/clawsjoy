FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY bin/requirements.txt ./bin/
RUN pip install --no-cache-dir -r bin/requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/

COPY bin/ ./bin/
COPY skills/ ./skills/
COPY web/ ./web/

RUN mkdir -p /app/logs /app/outbox

EXPOSE 8082 8084 8087

COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

RUN useradd -m -u 1000 clawsjoy && chown -R clawsjoy:clawsjoy /app
USER clawsjoy

CMD ["/docker-start.sh"]
