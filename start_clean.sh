#!/bin/bash
cd /mnt/d/clawsjoy

echo "🖥️ 启动 ClawsJoy 服务..."

# 启动网关
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
echo "  ✅ 网关 (5002)"

sleep 2

# 启动文件服务
python3 file_service_complete.py > logs/file.log 2>&1 &
echo "  ✅ 文件服务 (5003)"

sleep 1

# 启动多智能体
python3 multi_agent_service_v2.py > logs/multi.log 2>&1 &
echo "  ✅ 多智能体 (5005)"

sleep 1

# 启动文档服务
python3 doc_generator.py > logs/doc.log 2>&1 &
echo "  ✅ 文档服务 (5008)"

sleep 1

# 启动 Agent API
python3 agent_api.py > logs/agent_api.log 2>&1 &
echo "  ✅ Agent API (5010)"

sleep 1

# 启动 Web Dashboard
python3 web_server.py > logs/web.log 2>&1 &
echo "  ✅ Web Dashboard (5011)"

sleep 1

# 启动监控 API
python3 web/monitoring_api.py > logs/monitoring_api.log 2>&1 &
echo "  ✅ 监控 API (5021)"

echo ""
echo "✅ 所有服务已启动"
echo "📍 Web Dashboard: http://localhost:5011"
echo "📍 监控 API: http://localhost:5021"
