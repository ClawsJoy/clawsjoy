#!/bin/bash
# Docker 容器入口脚本

cd /app

echo "=========================================="
echo "🚀 ClawsJoy 4.0 容器启动"
echo "=========================================="

# 启动服务
python3 auth_service.py &
python3 driver_service_https.py &
python3 user_preference_service.py &
python3 web_dashboard_secure.py &

# 启动看门狗
python3 lib/agent_watchdog.py &

# 保持运行
wait
