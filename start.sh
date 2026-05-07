#!/bin/bash
# ClawsJoy 一键启动

set -e

cd /mnt/d/clawsjoy

echo "🦞 ClawsJoy 启动中..."

# 1. 启动 Docker 服务
echo "📦 启动 Docker 服务..."
docker-compose up -d web redis tts 2>/dev/null || echo "⚠️ Docker 服务已运行"

# 2. 启动 PM2 服务
echo "🚀 启动 API 服务..."
pm2 start bin/chat_api.py --interpreter python3 --name chat-api -- --port 18109 2>/dev/null
pm2 start bin/promo_api.py --interpreter python3 --name promo-api -- --port 8108 2>/dev/null
pm2 save 2>/dev/null

# 3. 检查服务状态
echo ""
echo "📊 服务状态:"
pm2 list

# 4. 健康检查
echo ""
echo "🩺 健康检查:"
sleep 2
curl -s -o /dev/null -w "Chat API: %{http_code}\n" http://localhost:18109/api/agent -X POST -d '{"text":"ping"}' -H "Content-Type: application/json"
curl -s -o /dev/null -w "Promo API: %{http_code}\n" http://localhost:8108/api/promo/make -X POST -d '{"city":"test"}' -H "Content-Type: application/json" 2>/dev/null
curl -s -o /dev/null -w "Web: %{http_code}\n" http://localhost:18083/

echo ""
echo "✅ ClawsJoy 启动完成"
echo "🌐 访问: http://localhost:18083/joymate/index.html?tenant=1"
