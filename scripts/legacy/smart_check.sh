#!/bin/bash
cd /mnt/d/clawsjoy

echo "🔍 ClawsJoy 智能检查"
echo "===================="
echo ""

# 1. 服务状态
echo "📡 服务状态:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "  ✅ :$port"
    else
        echo "  ❌ :$port"
    fi
done

# 2. 大脑统计
echo ""
echo "🧠 大脑统计:"
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
stats = brain.get_stats()
print(f'  经验: {stats.get(\"total_experiences\", 0)} 条')
print(f'  成功率: {stats.get(\"success_rate\", 0)*100:.1f}%')
" 2>/dev/null

# 3. 性能检查
echo ""
echo "📊 性能检查:"
python3 -c "
import psutil
print(f'  CPU: {psutil.cpu_percent()}%')
print(f'  内存: {psutil.virtual_memory().percent}%')
print(f'  磁盘: {psutil.disk_usage(\"/\").percent}%')
" 2>/dev/null

# 4. 日志错误检查
echo ""
echo "📋 日志错误检查:"
for log in logs/*.log; do
    if [ -f "$log" ]; then
        error_count=$(grep -ci "error\|fail\|exception" "$log" 2>/dev/null || echo 0)
        if [ "$error_count" -gt 0 ]; then
            echo "  ⚠️ $(basename $log): $error_count 个错误"
        fi
    fi
done

# 5. 智能推荐
echo ""
python3 intelligence/recommendation_engine.py 2>/dev/null

echo ""
echo "===================="
echo "✅ 检查完成"
