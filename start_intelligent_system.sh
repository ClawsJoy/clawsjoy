#!/bin/bash
cd /mnt/d/clawsjoy

echo "
╔═══════════════════════════════════════════════════════════════╗
║              🧠 ClawsJoy 智能系统启动器                        ║
╚═══════════════════════════════════════════════════════════════╝
"

# 创建必要目录
mkdir -p logs data intelligence

# 清理旧进程
echo "🧹 清理旧进程..."
pkill -f "agent_gateway|file_service|multi_agent|doc_generator|health_monitor|self_healer" 2>/dev/null
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

# 启动智能层
echo ""
echo "🧠 启动智能层..."

# 健康监控器
nohup python3 intelligence/health_monitor.py > logs/monitor.log 2>&1 &
echo "   ✅ 健康监控器"

# 自愈执行器
nohup python3 intelligence/self_healer.py > logs/healer.log 2>&1 &
echo "   ✅ 自愈执行器"

# 智能核心
nohup python3 intelligence/smart_core_v2.py > logs/smart_core.log 2>&1 &
echo "   ✅ 智能核心"

sleep 3

# 验证服务
echo ""
echo "📊 服务验证:"
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "   ✅ :$port"
    else
        echo "   ❌ :$port"
    fi
done

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ 智能系统已启动                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 日志位置:"
echo "   主网关: logs/gateway.log"
echo "   监控器: logs/monitor.log"
echo "   自愈器: logs/healer.log"
echo "   智能核心: logs/smart_core.log"
echo ""
echo "🔧 管理命令:"
echo "   查看状态: ./manage.sh status"
echo "   查看看板: ./manage.sh dashboard"
echo "   停止系统: ./manage.sh stop"
