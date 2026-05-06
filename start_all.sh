#!/bin/bash

echo "🚀 启动 ClawsJoy 所有服务..."

cd /mnt/d/clawsjoy

# 1. 启动 Docker 服务
echo "启动 Docker 容器..."
docker-compose up -d

# 2. 启动 Ollama（如果未运行）
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "启动 Ollama..."
    OLLAMA_HOST=0.0.0.0 nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
fi

# 3. 启动 Chat API（宿主机）
echo "启动 Chat API..."
pkill -f chat_api_agent 2>/dev/null
nohup python3 bin/chat_api_agent.py > /tmp/chat_api.log 2>&1 &

sleep 2

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📱 访问地址:"
echo "   聊天: http://localhost:8082/joymate/index.html"
echo "   编辑器: http://localhost:8082/joymate/editor.html"
echo "   资料库: http://localhost:8082/joymate/library.html"
echo "   首页: http://localhost:8082/index.html"
