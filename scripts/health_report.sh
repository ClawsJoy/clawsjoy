#!/bin/bash
cd /mnt/d/clawsjoy

echo "=========================================="
echo "ClawsJoy 健康报告 - $(date)"
echo "=========================================="

# 服务状态
echo ""
echo "📡 服务状态:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "  ✅ 端口 $port"
    else
        echo "  ❌ 端口 $port"
    fi
done

# 成功率（实时计算）
echo ""
echo "📊 成功率:"
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from lib.memory_simple import memory
outcomes = memory.recall_all(category='workflow_outcome')
total = len(outcomes)
success = len([o for o in outcomes if '成功' in o])
rate = success/total*100 if total else 0
print(f'  最近{total}次任务: {success}成功, {total-success}失败, 成功率{rate:.0f}%')
"

# 记忆统计
echo ""
echo "💾 记忆统计:"
python3 -c "
from lib.memory_simple import memory
cats = ['workflow_outcome', 'error_knowledge', 'calibration_log', 'executed_decisions']
for cat in cats:
    cnt = len(memory.recall_all(category=cat))
    print(f'  {cat}: {cnt}条')
"

# 智能进程
echo ""
echo "🤖 智能进程:"
ps aux | grep -E "intelligence|analyzer_daemon|decision_engine" | grep -v grep | wc -l | xargs echo "  运行中:"

echo ""
echo "=========================================="
