#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 启动 ClawsJoy 智能核心"
echo "================================"

# 启动智能核心（后台）
nohup python3 intelligence/smart_core.py > logs/smart_core.log 2>&1 &
SMART_PID=$!

echo "✅ 智能核心已启动 (PID: $SMART_PID)"
echo "📋 日志: logs/smart_core.log"
echo ""
echo "查看日志: tail -f logs/smart_core.log"
echo "停止: kill $SMART_PID"
