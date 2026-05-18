#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 启动大脑决策守护进程"
echo "========================"

# 检查是否已运行
if pgrep -f "decision_executor.py --daemon" > /dev/null; then
    echo "大脑守护进程已在运行"
    exit 0
fi

# 启动后台进程
nohup python3 intelligence/decision_executor.py --daemon > logs/brain_daemon.log 2>&1 &
BRAIN_PID=$!

echo "✅ 大脑守护进程已启动 (PID: $BRAIN_PID)"
echo "📋 决策间隔: 5分钟"
echo "📋 日志: logs/brain_daemon.log"
echo ""
echo "查看日志: tail -f logs/brain_daemon.log"
echo "停止进程: kill $BRAIN_PID"
