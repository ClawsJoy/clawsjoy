#!/bin/bash
cd /mnt/d/clawsjoy

clear
echo "
╔═══════════════════════════════════════════════════════════════╗
║                    ClawsJoy 系统状态                          ║
║                        $(date '+%H:%M:%S')                    ║
╚═══════════════════════════════════════════════════════════════╝
"

echo "📡 服务状态:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "  ✅ :$port"
    else
        echo "  ❌ :$port"
    fi
done

echo ""
echo "🧠 大脑统计:"
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
stats = brain.get_stats()
print(f'  经验: {stats.get(\"total_experiences\", 0)} 条')
print(f'  成功率: {stats.get(\"success_rate\", 0)*100:.1f}%')
print(f'  知识节点: {stats.get(\"knowledge_graph_nodes\", 0)} 个')
" 2>/dev/null

echo ""
echo "🤖 多智能体:"
curl -s http://localhost:5005/agents 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Agent数量: {len(d.get(\"agents\",[]))}')" 2>/dev/null

echo ""
echo "📁 生成的文件:"
ls -1 data/uploads/ 2>/dev/null | wc -l | xargs echo "  文件数量:"

echo ""
echo "═══════════════════════════════════════════════════════════════"
