#!/bin/bash
cd /mnt/d/clawsjoy

echo "🧠 ClawsJoy 完全智能增强版"
echo "=========================================="

# 创建日志目录
mkdir -p logs

# 清理可能冲突的进程
echo "🧹 清理旧进程..."
pkill -f "agent_gateway_web" 2>/dev/null
pkill -f "file_service_complete" 2>/dev/null
pkill -f "multi_agent_service" 2>/dev/null
pkill -f "doc_generator" 2>/dev/null
sleep 2

# 1. 启动原有服务
echo ""
echo "📡 启动基础服务..."
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
echo "   ✅ 主网关 (5002)"
python3 file_service_complete.py > logs/file.log 2>&1 &
echo "   ✅ 文件服务 (5003)"
python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &
echo "   ✅ 多智能体 (5005)"
python3 doc_generator.py > logs/doc.log 2>&1 &
echo "   ✅ 文档生成 (5008)"

sleep 5

# 2. 启动智能层
echo ""
echo "🧠 启动智能层..."

# 监控器（后台）
python3 intelligence/monitor.py > logs/monitor.log 2>&1 &
echo "   ✅ 智能监控器"

# 调度器（后台）
python3 intelligence/scheduler.py > logs/scheduler.log 2>&1 &
echo "   ✅ 智能调度器"

# 学习器（运行一次）
python3 intelligence/learner.py
echo "   ✅ 智能学习器"

# 分析器（生成报告）
python3 intelligence/analyzer.py

echo ""
echo "=========================================="
echo "✅ ClawsJoy 完全智能增强版已启动"
echo ""
echo "服务地址:"
echo "  🌐 主网关: http://localhost:5002"
echo "  📁 文件服务: http://localhost:5003"
echo "  🤖 多智能体: http://localhost:5005"
echo "  📝 文档生成: http://localhost:5008"
echo ""
echo "智能层:"
echo "  🔍 监控器 (logs/monitor.log)"
echo "  📋 调度器 (logs/scheduler.log)"
echo "  📊 分析器 (data/intelligence_report.json)"
echo "  📚 学习器 (logs/learning.log)"
echo "=========================================="

# 显示健康状态
sleep 2
echo ""
curl -s http://localhost:5002/api/health | python3 -m json.tool
