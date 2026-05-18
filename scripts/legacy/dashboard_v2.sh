#!/bin/bash
cd /mnt/d/clawsjoy

clear
echo "
╔═══════════════════════════════════════════════════════════════════╗
║                    🧠 ClawsJoy 智能看板 V2                         ║
║                         $(date '+%Y-%m-%d %H:%M:%S')                           ║
╚═══════════════════════════════════════════════════════════════════╝
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
echo "🧠 大脑状态:"
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
stats = brain.get_stats()
print(f'  经验: {stats.get(\"total_experiences\", 0)} 条')
print(f'  成功率: {stats.get(\"success_rate\", 0)*100:.1f}%')
print(f'  知识图谱: {stats.get(\"knowledge_graph_nodes\", 0)} 个')
"

echo ""
echo "🔧 运行中的进程:"
ps aux | grep -E "agent_gateway|file_service|multi_agent|doc_generator" | grep -v grep | wc -l | xargs echo "  活跃进程数:"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
