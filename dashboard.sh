#!/bin/bash
clear
echo "
╔═══════════════════════════════════════════════════════════════╗
║                    🧠 ClawsJoy 智能看板                        ║
║                         $(date '+%Y-%m-%d %H:%M:%S')                          ║
╚═══════════════════════════════════════════════════════════════╝
"

# 服务状态
echo "📡 服务状态:"
for service in "主网关:5002" "文件服务:5003" "多智能体:5005" "文档生成:5008"; do
    name=${service%:*}
    port=${service#*:}
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "  ✅ $name (:$port)"
    else
        echo "  ❌ $name (:$port)"
    fi
done

# 智能报告
echo ""
python3 intelligence/analyzer.py 2>/dev/null

# 预测
echo ""
python3 intelligence/predictor.py 2>/dev/null

# 进程
echo ""
echo "🔧 运行中的进程:"
ps aux | grep -E "agent_gateway|file_service|multi_agent|doc_generator|smart_core" | grep -v grep | wc -l | xargs echo "  活跃进程数:"

echo ""
echo "═══════════════════════════════════════════════════════════════"
