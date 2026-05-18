#!/bin/bash
cd /mnt/d/clawsjoy

echo "🚀 启动 ClawsJoy 智能增强版"
echo "================================"

# 启动原有服务
echo "📡 启动主网关..."
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &

echo "📁 启动文件服务..."
python3 file_service_complete.py > logs/file.log 2>&1 &

echo "🤖 启动多智能体..."
python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &

sleep 3

# 可选：启动智能层（旁路）
read -p "是否启动智能监控器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 intelligence/monitor.py &
    echo "✅ 智能监控器已启动"
fi

echo ""
echo "✅ 启动完成"
echo "访问: http://localhost:5002"
