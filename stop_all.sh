#!/bin/bash
# ClawsJoy 4.0 停止脚本

echo "=========================================="
echo "🛑 ClawsJoy 4.0 停止"
echo "=========================================="

pkill -f "auth_service" 2>/dev/null && echo "   ✅ 认证服务"
pkill -f "driver_service" 2>/dev/null && echo "   ✅ 驱动服务"
pkill -f "user_preference" 2>/dev/null && echo "   ✅ 偏好服务"
pkill -f "web_dashboard_secure" 2>/dev/null && echo "   ✅ 安全Web"
pkill -f "agent_watchdog" 2>/dev/null && echo "   ✅ 看门狗"
pkill -f "monitor_alert" 2>/dev/null && echo "   ✅ 监控"

echo ""
echo "✅ 所有服务已停止"
