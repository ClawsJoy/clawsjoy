#!/bin/bash
# 安全启动网关

cd /home/flybo/clawsjoy_v5

# 停止旧进程
if [ -f logs/gateway.pid ]; then
    OLD_PID=$(cat logs/gateway.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "停止旧进程: $OLD_PID"
        kill -9 $OLD_PID 2>/dev/null
    fi
    rm -f logs/gateway.pid
fi

# 清理僵尸进程
sudo pkill -9 -f agent_gateway_enhanced 2>/dev/null || true

# 等待
sleep 2

# 启动（使用低优先级避免OOM）
echo "启动网关..."
nohup nice -n 10 python3 -u agent_gateway_enhanced.py > logs/gateway.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > logs/gateway.pid

echo "✅ 网关已启动，PID: $NEW_PID"
echo "查看日志: tail -f logs/gateway.log"

# 等待启动
sleep 5

# 检查状态
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ 网关运行正常"
    # 测试
    curl -s -X POST http://localhost:5002/v5/execute \
        -H "Content-Type: application/json" \
        -d '{"raw_input": "ping", "action": "chat", "user_id": "test"}' \
        | python3 -m json.tool | head -10
else
    echo "❌ 网关启动失败，查看日志:"
    tail -20 logs/gateway.log
fi
