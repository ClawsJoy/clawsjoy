#!/bin/bash
# ClawsJoy 协程模式（高并发 I/O）

cd /mnt/d/clawsjoy_clean

# 使用 Gevent worker（适合大量 I/O 等待）
echo "🚀 启动 ClawsJoy 协程模式"
echo "   Worker: gevent"
echo "📍 http://localhost:5002"

gunicorn src.api.gateway:app \
    --workers 4 \
    --worker-class gevent \
    --bind 0.0.0.0:5002 \
    --timeout 120
