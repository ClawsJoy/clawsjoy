#!/bin/bash
cd /mnt/d/clawsjoy

echo "
╔══════════════════════════════════════════════════════════╗
║     🧠 ClawsJoy 智能增强版 - 渐进式升级                  ║
║                   稳定运行版                             ║
╚══════════════════════════════════════════════════════════╝
"

mkdir -p logs

# 清理所有相关进程
echo "🧹 清理旧进程..."
pkill -9 -f "agent_gateway_web" 2>/dev/null
pkill -9 -f "file_service_complete" 2>/dev/null
pkill -9 -f "multi_agent_service" 2>/dev/null
pkill -9 -f "doc_generator" 2>/dev/null
sleep 2

# 启动服务
echo ""
echo "📡 启动基础服务..."

# 1. 主网关 (5002)
nohup python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   ✅ 主网关      (5002) PID: $GATEWAY_PID"

# 2. 文件服务 (5003)
nohup python3 file_service_complete.py > logs/file.log 2>&1 &
FILE_PID=$!
echo "   ✅ 文件服务    (5003) PID: $FILE_PID"

# 3. 多智能体 (5005)
nohup python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &
AGENT_PID=$!
echo "   ✅ 多智能体    (5005) PID: $AGENT_PID"

# 4. 文档生成 (5008)
nohup python3 doc_generator.py > logs/doc.log 2>&1 &
DOC_PID=$!
echo "   ✅ 文档生成    (5008) PID: $DOC_PID"

sleep 5

# 健康检查
echo ""
echo "📊 健康检查:"

ALL_OK=true
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "   ✅ :$port"
    else
        echo "   ❌ :$port"
        ALL_OK=false
    fi
done

# 显示 PID 文件
echo ""
echo "📝 PID 文件:"
echo "   $GATEWAY_PID > logs/gateway.pid"
echo "   $FILE_PID > logs/file.pid"
echo "   $AGENT_PID > logs/agent.pid"
echo "   $DOC_PID > logs/doc.pid"

# 智能分析
echo ""
python3 intelligence/analyzer.py 2>/dev/null

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
if [ "$ALL_OK" = true ]; then
    echo "║              ✅ ClawsJoy 已就绪！                       ║"
else
    echo "║              ⚠️ 部分服务异常，请检查日志                ║"
fi
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 访问: http://localhost:5002"
echo "📋 日志: logs/ 目录"
echo ""
echo "停止服务: pkill -f 'agent_gateway|file_service|multi_agent|doc_generator'"
