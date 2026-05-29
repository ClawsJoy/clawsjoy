#!/bin/bash
# 停止所有开发服务

echo "🛑 停止 ClawsJoy 开发服务..."

pkill -9 -f "gunicorn.*5002" 2>/dev/null
pkill -9 -f "gunicorn.*5003" 2>/dev/null

sleep 2

echo "✅ 服务已停止"
