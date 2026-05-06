#!/bin/bash
# ClawsJoy 一键安装脚本

set -e

echo "🦞 ClawsJoy 一键安装"
echo "===================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

# 克隆仓库
if [ ! -d "ClawsJoy" ]; then
    echo "📦 克隆仓库..."
    git clone https://github.com/ClawsJoy/ClawsJoy.git
fi

cd ClawsJoy

# 创建必要目录
mkdir -p tenants/template/config
mkdir -p data logs web/videos web/images web/audio

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 启动额外服务
cd bin
nohup python3 promo_api.py > /tmp/promo.log 2>&1 &
nohup python3 chat_api_agent.py > /tmp/chat.log 2>&1 &
nohup python3 agent_api.py > /tmp/agent.log 2>&1 &
cd ..

echo ""
echo "✅ 安装完成！"
echo ""
echo "🌐 访问: http://localhost:18082/joymate/index.html?tenant=1"
echo "📝 默认租户ID: 1"
echo ""
echo "📖 文档: https://github.com/ClawsJoy/ClawsJoy"
