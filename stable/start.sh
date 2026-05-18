#!/bin/bash
# ClawsJoy 稳定版启动脚本

cd /mnt/d/clawsjoy/stable

echo "启动 ClawsJoy 稳定版..."

# 启动任务调度器
cd bin
python3 task_api.py &
TASK_PID=$!
echo "✅ 任务调度器启动 (PID: $TASK_PID)"

# 启动 Web 服务
cd /mnt/d/clawsjoy/web
python3 -m http.server 8082 &
WEB_PID=$!
echo "✅ Web 服务启动 (PID: $WEB_PID)"

# 保存 PID
echo "$TASK_PID" > /tmp/clawsjoy_task.pid
echo "$WEB_PID" > /tmp/clawsjoy_web.pid

echo ""
echo "=========================================="
echo "🎉 ClawsJoy 稳定版已启动"
echo "🌐 访问: http://localhost:8082/joymate/?tenant=1"
echo "🔐 账号: admin / admin123"
echo "=========================================="
