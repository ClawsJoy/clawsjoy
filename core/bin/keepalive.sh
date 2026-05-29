#!/bin/bash
# 服务守护脚本 - 确保服务持续运行

check_and_restart() {
    local name=$1
    local port=$2
    local check_cmd=$3
    
    if ! eval "$check_cmd" 2>/dev/null; then
        echo "[$(date)] $name 异常，正在重启..."
        pm2 restart $name 2>/dev/null || pm2 start $name
        sleep 3
        return 1
    fi
    return 0
}

# 每分钟检查一次
while true; do
    check_and_restart "chat-api" "18109" "curl -s -X POST http://localhost:18109/api/agent -d '{\"text\":\"ping\"}' -H 'Content-Type: application/json' | grep -q message"
    check_and_restart "promo-api" "8108" "curl -s -X POST http://localhost:8108/api/promo/make -d '{\"city\":\"test\"}' -H 'Content-Type: application/json' | grep -q success"
    check_and_restart "web" "18083" "curl -s http://localhost:18083/ -o /dev/null -w '%{http_code}' | grep -q 200"
    
    sleep 60
done
