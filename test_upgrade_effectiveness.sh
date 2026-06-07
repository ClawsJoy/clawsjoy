#!/bin/bash
# 测试升级效果

echo "📊 ClawsJoy Agent 性能对比"
echo "=========================="

for agent in chat_agent code_agent vision_agent; do
    echo ""
    echo "🔍 $agent:"
    
    # 查看当前配置
    temp=$(grep "temperature:" agents/$agent/config.yaml | head -1 | awk '{print $2}')
    echo "   temperature: $temp"
    
    # 查看升级历史
    echo "   最近升级记录:"
    python3 -c "
import json
with open('data/upgrades/upgrade_history.json', 'r') as f:
    history = json.load(f)
    records = [h for h in history if h['agent'] == '$agent']
    if records:
        last = records[-1]
        print(f\"     时间: {last['timestamp'][:19]}\")
        print(f\"     升级前成功率: {last['success_rate_before']:.1%}\")
        print(f\"     改进: {last['suggestions']}\")
    else:
        print(\"     无升级记录\")
"
done

echo ""
echo "📈 实时性能监控:"
python3 -c "
from tools.real_log_collector import RealLogCollector
collector = RealLogCollector()
for agent in ['chat_agent', 'code_agent', 'vision_agent']:
    stats = collector.get_performance_stats(agent, hours=1)
    print(f\"{agent}: {stats['success_rate']:.1%} ({stats['total']}次交互)\")
"
