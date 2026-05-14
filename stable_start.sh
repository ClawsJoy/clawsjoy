#!/bin/bash
cd /mnt/d/clawsjoy

# 清理
pkill -9 -f "agent_gateway\|file_service\|multi_agent\|doc_generator" 2>/dev/null
sleep 2

# 清理端口
for port in 5002 5003 5005 5008; do
    kill -9 $(lsof -t -i:$port) 2>/dev/null
done

sleep 1

# 启动
mkdir -p logs
python3 agent_gateway_web.py > logs/gateway.log 2>&1 &
echo "主网关: $!"
python3 file_service_complete.py > logs/file.log 2>&1 &
echo "文件服务: $!"
python3 multi_agent_service_v2.py > logs/agent.log 2>&1 &
echo "多智能体: $!"
python3 doc_generator.py > logs/doc.log 2>&1 &
echo "文档生成: $!"

sleep 5

echo ""
echo "服务状态:"
curl -s http://localhost:5002/api/health 2>/dev/null | python3 -m json.tool 2>/dev/null
curl -s http://localhost:5005/agents 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'多智能体: {len(d.get(\"agents\",[]))} 个Agent')" 2>/dev/null
