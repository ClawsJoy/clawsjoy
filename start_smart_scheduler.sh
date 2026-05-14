#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 启动智能调度器"
python3 agents/smart_scheduler.py &
echo $! > logs/smart_scheduler.pid
echo "✅ 智能调度器已启动 (PID: $(cat logs/smart_scheduler.pid))"
