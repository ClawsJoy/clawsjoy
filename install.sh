#!/bin/bash
# ClawsJoy 一键安装脚本

echo "🦞 ClawsJoy 安装脚本"
echo "===================="

# 安装依赖
echo "📦 安装依赖..."
sudo apt update
sudo apt install -y python3 python3-pip redis-server curl git

# 安装 Python 包
pip3 install redis requests pyyaml flask flask-cors --break-system-packages

# 安装 Ollama
if ! command -v ollama &> /dev/null; then
    echo "📦 安装 Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull qwen2.5:3b
fi

# 启动 Redis
sudo systemctl start redis-server

# 启动 ClawsJoy
cd /home/flybo/clawsjoy
bash bin/start_clawsjoy.sh

echo ""
echo "✅ 安装完成！"
echo "🌐 访问: http://localhost:8082/tenant/"
echo "🔐 默认账号: admin / admin123"
