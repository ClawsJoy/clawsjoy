#!/bin/bash
# ClawsJoy 稳定版停止脚本

echo "停止 ClawsJoy 服务..."

# 读取 PID 并停止
if [ -f /tmp/clawsjoy_task.pid ]; then
    kill $(cat /tmp/clawsjoy_task.pid) 2>/dev/null
    rm /tmp/clawsjoy_task.pid
    echo "✅ 任务调度器已停止"
fi

if [ -f /tmp/clawsjoy_web.pid ]; then
    kill $(cat /tmp/clawsjoy_web.pid) 2>/dev/null
    rm /tmp/clawsjoy_web.pid
    echo "✅ Web 服务已停止"
fi

# 清理残留进程
pkill -f "task_api.py" 2>/dev/null
pkill -f "http.server 8082" 2>/dev/null

echo "✅ 所有服务已停止"
