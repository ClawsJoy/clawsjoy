#!/bin/bash
# 服务健康检查
for port in 5002 5003 5005 5008; do
    if ! curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "$(date): 端口 $port 异常，尝试重启"
        case $port in
            5002) cd /mnt/d/clawsjoy && nohup python3 agent_gateway_web.py > logs/gateway.log 2>&1 & ;;
            5003) cd /mnt/d/clawsjoy && nohup python3 file_service_complete.py > logs/file.log 2>&1 & ;;
            5005) cd /mnt/d/clawsjoy && nohup python3 multi_agent_service_v2.py > logs/agent.log 2>&1 & ;;
            5008) cd /mnt/d/clawsjoy && nohup python3 doc_generator.py > logs/doc.log 2>&1 & ;;
        esac
    fi
done
