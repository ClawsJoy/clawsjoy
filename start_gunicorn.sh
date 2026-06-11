#!/bin/bash
# 使用 Gunicorn 启动网关（高并发）

cd "$(dirname "$0")"

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🚀 启动 ClawsJoy Gateway (Gunicorn)"

# 停止旧进程
pkill -f "gunicorn.*clawsjoy" 2>/dev/null
pkill -f "agent_gateway_enhanced" 2>/dev/null

# 启动 Gunicorn
gunicorn -c gunicorn.conf.py agent_gateway_enhanced:app

echo "✅ 服务已启动"
