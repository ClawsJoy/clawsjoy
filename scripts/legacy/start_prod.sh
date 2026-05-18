#!/bin/bash
# ClawsJoy 生产模式启动（多进程）

cd /mnt/d/clawsjoy_clean

# 使用 Gunicorn 启动（4个 worker 进程）
echo "🚀 启动 ClawsJoy 生产模式"
echo "   Workers: 4"
echo "   线程: 2 per worker"
echo "📍 http://localhost:5002"

gunicorn src.api.gateway:app \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --bind 0.0.0.0:5002 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
