#!/bin/bash
cd /home/flybo/clawsjoy_clean
source .env.production 2>/dev/null

# 停止旧进程
pkill -f gunicorn 2>/dev/null
sleep 1

# 启动 gunicorn
nohup gunicorn -w ${GUNICORN_WORKERS:-4} \
         -k gevent \
         --worker-connections ${GUNICORN_WORKER_CONNECTIONS:-1000} \
         --threads ${GUNICORN_THREADS:-2} \
         --bind 0.0.0.0:5002 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         agent_gateway_web:app >> logs/gateway.log 2>&1 &

echo "✅ 生产服务已启动 (PID: $!)"
sleep 2
curl -s http://localhost:5002/api/health
