#!/bin/bash
# ClawsJoy 每日分析师报告

cd /mnt/d/clawsjoy_clean

echo "=========================================="
echo "ClawsJoy 分析师报告 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 1. 统一分析
echo ""
echo "📊 统一分析结果:"
python3 -c "
import sys
sys.path.insert(0, '.')
from intelligence.unified_analyzer import UnifiedAnalyzer
analyzer = UnifiedAnalyzer()
result = analyzer.analyze()
print(f'  成功率: {result.get(\"success_rate\", \"N/A\")}')
print(f'  关键问题: {result.get(\"critical_issues\", [])[:2]}')
"

# 2. 大脑状态
echo ""
echo "🧠 大脑学习状态:"
python3 -c "
import sys
sys.path.insert(0, '.')
import json
with open('data/brain_v2.json', 'r') as f:
    brain = json.load(f)
stats = brain.get('stats', {})
total = stats.get('total_actions', 0)
success = stats.get('successful', 0)
print(f'  总经验: {total}')
print(f'  成功: {success} ({success/total*100:.1f}%)' if total else '  无数据')
print(f'  知识图谱: {len(brain.get(\"knowledge_graph\", []))} 节点'
"

# 3. 服务状态
echo ""
echo "🔌 服务状态:"
for port in 5002 5005 8188; do
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "  ✅ 端口 $port - 正常"
    else
        echo "  ❌ 端口 $port - 异常"
    fi
done

# 4. 监控告警
echo ""
echo "📊 监控告警:"
tail -5 logs/success_monitor.log 2>/dev/null | grep -E "🟡|🔴" | tail -3

echo ""
echo "=========================================="
echo "✅ 报告完成 - $(date '+%Y-%m-%d %H:%M:%S')"
