#!/bin/bash
cd /mnt/d/clawsjoy

echo "🚀 启动 ClawsJoy 所有服务..."

# 启动网关
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
echo "  ✅ 网关 (5002)"

# 启动文件服务
python3 file_service_complete.py > logs/file.log 2>&1 &
echo "  ✅ 文件服务 (5003)"

# 启动多智能体
python3 multi_agent_service_v2.py > logs/multi.log 2>&1 &
echo "  ✅ 多智能体 (5005)"

# 启动文档服务
python3 doc_generator.py > logs/doc.log 2>&1 &
echo "  ✅ 文档服务 (5008)"

# 启动 Agent API
python3 agent_api.py > logs/agent_api.log 2>&1 &
echo "  ✅ Agent API (5010)"

# 启动 Web Dashboard
python3 web_server.py > logs/web.log 2>&1 &
echo "  ✅ Web Dashboard (5011)"

# 启动监控 API
python3 web/monitoring_api.py > logs/monitoring_api.log 2>&1 &
echo "  ✅ 监控 API (5021)"

# 启动注册中心
python3 web/registry_api.py > logs/registry_api.log 2>&1 &
echo "  ✅ 注册中心 (5022)"

# 启动定时任务 API
python3 web/task_api.py > logs/task_api.log 2>&1 &
echo "  ✅ 定时任务 API (5023)"

# 启动技能市场 API
python3 web/market_api.py > logs/market_api.log 2>&1 &
echo "  ✅ 技能市场 API (5024)"

sleep 3
echo ""
echo "✅ 所有服务已启动"
echo ""
echo "📍 访问地址:"
echo "   API Gateway:    http://localhost:5002"
echo "   Web Dashboard:  http://localhost:5011"
echo "   注册中心:       http://localhost:5022"
echo "   定时任务:       http://localhost:5023"
echo "   技能市场:       http://localhost:5024"
echo "   API 文档:       http://localhost:5002/apidocs"
echo "   Metrics:        http://localhost:5002/metrics"
