#!/bin/bash
cd /mnt/d/clawsjoy

echo "🛑 停止 ClawsJoy 服务"

# 停止监控
if [ -f logs/event_monitor.pid ]; then
    kill $(cat logs/event_monitor.pid) 2>/dev/null
    rm logs/event_monitor.pid
fi

# 停止网关
pkill -f agent_gateway_web

echo "✅ 所有服务已停止"
