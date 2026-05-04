#!/bin/bash
set -e
echo "🦞 ClawsJoy 一键安装"
echo "===================="
if ! command -v docker &> /dev/null; then
    echo "请先安装 Docker"
    exit 1
fi
if [ ! -d "clawsjoy" ]; then
    git clone https://github.com/ClawsJoy/ClawsJoy.git clawsjoy
fi
cd clawsjoy
docker-compose up -d
echo ""
echo "✅ 安装完成！"
echo "🌐 访问: http://localhost:8082/tenant/"
echo "🔐 账号: admin / admin123"
