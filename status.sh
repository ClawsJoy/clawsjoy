#!/bin/bash
cd /mnt/d/clawsjoy

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    ClawsJoy 系统状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 服务状态
echo "📡 服务状态:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "   ✅ :$port"
    else
        echo "   ❌ :$port"
    fi
done

# 智能层进程
echo ""
echo "🧠 智能层进程:"
for proc in "health_monitor" "self_healer" "smart_core_v2"; do
    if pgrep -f "$proc" > /dev/null; then
        echo "   ✅ $proc"
    else
        echo "   ❌ $proc"
    fi
done

# 大脑统计
echo ""
echo "🧠 大脑统计:"
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
stats = brain.get_stats()
print(f'   经验: {stats.get(\"total_experiences\", 0)} 条')
print(f'   成功率: {stats.get(\"success_rate\", 0)*100:.1f}%')
print(f'   知识节点: {stats.get(\"knowledge_graph_nodes\", 0)} 个')
" 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
