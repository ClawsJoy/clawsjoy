#!/bin/bash

echo "🛑 停止 ClawsJoy 所有服务..."

cd /mnt/d/clawsjoy

# 停止 Docker 服务
echo "停止 Docker 容器..."
docker-compose down

# 停止 Chat API
echo "停止 Chat API..."
pkill -f chat_api_agent 2>/dev/null

echo "✅ 所有服务已停止"
