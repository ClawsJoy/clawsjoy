#!/bin/bash
echo "=== ClawsJoy 健康检查 ==="
echo "时间: $(date)"
echo ""

# 服务检查
for service in "主网关:5002" "文件服务:5003" "多智能体:5005" "文档生成:5008"; do
    name=${service%:*}
    port=${service#*:}
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "✅ $name (:$port)"
    else
        echo "❌ $name (:$port) - 异常"
    fi
done

# 智能分析
echo ""
python3 intelligence/analyzer.py 2>/dev/null

# 进程检查
echo ""
echo "=== 运行中的进程 ==="
ps aux | grep -E "agent_gateway|file_service|multi_agent|doc_generator" | grep -v grep | awk '{print "  " $11 " (PID:" $2 ")"}'
