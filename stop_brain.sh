#!/bin/bash
echo "🧠 停止大脑守护进程"
pkill -f "decision_executor.py --daemon"
echo "✅ 已停止"
