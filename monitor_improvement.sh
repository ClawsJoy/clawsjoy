#!/bin/bash
# 监控优化后的效果

echo "📈 监控性能改进 (每30秒刷新，按Ctrl+C退出)"
echo ""

while true; do
    clear
    echo "========================================"
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"
    
    cd /home/flybo/clawsjoy_v5
    
    python3 -c "
from tools.real_log_collector import RealLogCollector
c = RealLogCollector()
print('\n📊 最近1小时性能:')
for agent in ['chat_agent', 'code_agent', 'vision_agent']:
    stats = c.get_performance_stats(agent, hours=1)
    rate = stats['success_rate']
    icon = '🟢' if rate >= 0.8 else '🟡' if rate >= 0.6 else '🔴'
    print(f'{icon} {agent:15} {rate:5.1%} ({stats[\"total\"]:3}次)')
    
    # 显示超时情况
    timeouts = sum(1 for log in c.collect_agent_logs(agent, 1) 
                   if 'timeout' in str(log.get('error', '')).lower())
    if timeouts > 0:
        print(f'   ⚠️  超时: {timeouts}次')
"
    
    echo ""
    echo "按 Ctrl+C 退出监控"
    sleep 30
done
