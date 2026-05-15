#!/bin/bash
# 一键启动所有核心服务

cd /mnt/d/clawsjoy

echo "🚀 启动 ClawsJoy 核心服务..."

# 1. 启动 Docker 服务
docker-compose up -d web redis tts 2>/dev/null

# 2. 启动 API 服务
cd bin

# Chat API
if ! pm2 list | grep -q "chat-api"; then
    pm2 start chat_api.py --interpreter python3 --name chat-api -- --port 18109
fi

# Promo API
if ! pm2 list | grep -q "promo-api"; then
    pm2 start promo_api.py --interpreter python3 --name promo-api -- --port 8108
fi

# Agent API
if ! pm2 list | grep -q "agent-api"; then
    pm2 start agent_api.py --interpreter python3 --name agent-api -- --port 18103 2>/dev/null
fi

# Health API
if ! pm2 list | grep -q "health-api"; then
    pm2 start health_api.py --interpreter python3 --name health-api 2>/dev/null
fi

pm2 save
cd ..

echo -e "\n📊 服务状态:"
pm2 list | grep -E "online|errored"

echo -e "\n✅ 启动完成"
