#!/bin/bash
# 持续训练脚本

echo "🤖 启动持续训练..."
echo "每 5 分钟训练 10 次"

while true; do
    echo ""
    echo "=========================================="
    echo "训练轮次: $(date)"
    echo "=========================================="
    
    python3 scripts/train_agent_simple.py 2>/dev/null
    
    echo ""
    echo "等待 5 分钟..."
    sleep 300
done
