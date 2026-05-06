#!/bin/bash
# ClawsJoy 一键安装脚本

set -e

echo "🦞 ClawsJoy 一键安装"
echo "===================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

# 克隆仓库（如果不在仓库中）
if [ ! -f "docker-compose.yml" ]; then
    echo "📦 克隆仓库..."
    git clone https://github.com/ClawsJoy/clawsjoy.git .
fi

# 创建目录
mkdir -p tenants/template/config data logs web/videos web/images web/audio

# 启动 Docker 服务
echo "🚀 启动 Docker 服务..."
docker-compose up -d

# 等待 Docker 服务就绪
sleep 5

# 启动额外服务（宿主机）
echo "🚀 启动额外服务..."
cd bin
nohup python3 promo_api.py > /tmp/promo.log 2>&1 &
nohup python3 chat_api_agent.py > /tmp/chat.log 2>&1 &
if [ -f "agent_api.py" ]; then
    nohup python3 agent_api.py > /tmp/agent.log 2>&1 &
fi
cd ..

echo ""
echo "✅ 安装完成！"
echo ""
echo "🌐 Web 界面: http://localhost:18082/joymate/index.html?tenant=1"
echo "💬 Chat API: http://localhost:18101/api/agent"
echo "🎬 Promo API: http://localhost:8108/api/promo/make"
echo ""
echo "📖 文档: https://github.com/ClawsJoy/clawsjoy"
