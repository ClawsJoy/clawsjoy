#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧬 启动进化型大脑"
echo "=================="

# 停止旧的大脑
pkill -f "evolutionary_brain" 2>/dev/null
pkill -f "true_brain" 2>/dev/null

# 启动新大脑
python3 intelligence/evolutionary_brain.py &
BRAIN_PID=$!

echo ""
echo "✅ 进化型大脑已启动 (PID: $BRAIN_PID)"
echo ""
echo "🧬 自主进化模块:"
echo "   🔄 感知模块 - 实时监控"
echo "   🧠 决策模块 - 自主决策"
echo "   📚 学习模块 - 持续学习"
echo "   💡 创新模块 - 尝试新方法"
echo "   🧬 进化模块 - 自我进化"
echo ""
echo "查看: tail -f logs/evolution.log"
echo "停止: kill $BRAIN_PID"
