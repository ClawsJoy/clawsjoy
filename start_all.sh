#!/bin/bash
cd /mnt/d/clawsjoy

echo "🦞 启动 ClawsJoy 全套服务"

# 启动 API 网关
python3 agent_gateway_web.py &
echo "✅ API 网关已启动"

# 等待网关启动
sleep 3

# 启动事件监控（后台）
python3 agents/event_monitor.py > logs/event_monitor.log 2>&1 &
echo "✅ 事件监控已启动"

# 记录 PID
echo $! > logs/event_monitor.pid

echo ""
echo "📊 服务状态:"
echo "   API: http://localhost:5002"
echo "   监控: 正在运行"
echo ""
echo "停止服务: ./stop_all.sh"
