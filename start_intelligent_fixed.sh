#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 ClawsJoy 智能增强版 (稳定版)"
echo "=========================================="

mkdir -p logs

# 清理
echo "🧹 清理旧进程..."
pkill -9 -f "agent_gateway_web" 2>/dev/null
pkill -9 -f "file_service_complete" 2>/dev/null
pkill -9 -f "multi_agent_service" 2>/dev/null
pkill -9 -f "doc_generator" 2>/dev/null
sleep 2

# 启动基础服务
echo ""
echo "📡 启动基础服务..."
nohup python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
echo "   ✅ 主网关 (5002)"

nohup python3 file_service_complete.py > logs/file.log 2>&1 &
echo "   ✅ 文件服务 (5003)"

nohup python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &
echo "   ✅ 多智能体 (5005)"

nohup python3 doc_generator.py > logs/doc.log 2>&1 &
echo "   ✅ 文档生成 (5008)"

sleep 5

# 验证
echo ""
echo "📊 服务状态:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "   ✅ :$port"
    else
        echo "   ❌ :$port"
    fi
done

# 智能分析
echo ""
python3 intelligence/analyzer.py

echo ""
echo "=========================================="
echo "✅ 启动完成"
echo "=========================================="
