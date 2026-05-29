#!/bin/bash
# ClawsJoy v5.0.0 停止脚本

echo "=========================================="
echo "🛑 ClawsJoy 停止"
echo "=========================================="

pkill -f "gunicorn.*agent_gateway_web" 2>/dev/null && echo "✅ 已停止主网关"
pkill -f "auth_service\|driver_service\|user_preference\|web_dashboard_secure\|agent_watchdog" 2>/dev/null

sleep 2
echo "✅ 所有服务已停止"
