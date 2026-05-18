#!/bin/bash
cd /mnt/d/clawsjoy

echo "重启所有服务..."

# 停止
pkill -f "agent_gateway_web" 2>/dev/null
pkill -f "file_service_complete" 2>/dev/null
pkill -f "multi_agent_service" 2>/dev/null
pkill -f "doc_generator" 2>/dev/null
sleep 2

# 启动
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
python3 file_service_complete.py > logs/file.log 2>&1 &
python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &
python3 doc_generator.py > logs/doc.log 2>&1 &

sleep 5

echo "服务已启动"
curl -s http://localhost:5002/api/health | python3 -m json.tool
