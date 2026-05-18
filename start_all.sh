#!/bin/bash
# ClawsJoy 4.0 一键启动

cd /mnt/d/clawsjoy_clean
mkdir -p logs

echo "=========================================="
echo "🚀 ClawsJoy 4.0 启动"
echo "=========================================="

# 清理
pkill -f "auth_service\|driver_service\|user_preference\|web_dashboard_secure\|agent_watchdog" 2>/dev/null
sleep 2

# 启动服务
echo "启动认证服务..."
python3 auth_service.py > logs/auth.log 2>&1 &
echo "启动驱动服务..."
python3 driver_service_https.py > logs/driver.log 2>&1 &
echo "启动偏好服务..."
python3 user_preference_service.py > logs/preference.log 2>&1 &
echo "启动安全Web..."
python3 web_dashboard_secure.py > logs/web_secure.log 2>&1 &

sleep 3

# 启动监控
echo "启动监控告警..."
python3 -c "from lib.monitor_alert import monitor; monitor.start_monitor()" &

echo "启动看门狗..."
python3 lib/agent_watchdog.py &

echo ""
echo "=========================================="
echo "✅ ClawsJoy 4.0 启动完成"
echo "=========================================="
echo "访问: https://localhost:5446"
echo "账号: user1 / admin123"
echo "=========================================="
