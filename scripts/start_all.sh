#!/bin/bash
# ClawsJoy v5.0.0 一键启动

cd /home/flybo/clawsjoy_clean
mkdir -p logs

echo "=========================================="
echo "🚀 ClawsJoy v5.0.0 启动"
echo "=========================================="

# 停止旧进程
pkill -f "gunicorn.*agent_gateway_web" 2>/dev/null
pkill -f "auth_service\|driver_service\|user_preference\|web_dashboard_secure\|agent_watchdog" 2>/dev/null
sleep 2

# 加载环境变量
source .env.production 2>/dev/null

# 配置
WORKERS=${GUNICORN_WORKERS:-2}
CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-1000}
PORT=${GATEWAY_PORT:-5002}

echo "配置: workers=$WORKERS, connections=$CONNECTIONS, port=$PORT"

# 启动主网关
echo "启动主网关..."
gunicorn -w $WORKERS \
    -k gevent \
    --worker-connections $CONNECTIONS \
    --bind 0.0.0.0:$PORT \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    agent_gateway_web:app

sleep 3

# 健康检查
if curl -s http://localhost:$PORT/api/health > /dev/null 2>&1; then
    echo "✅ 主网关启动成功"
    curl -s http://localhost:$PORT/api/health | python3 -m json.tool 2>/dev/null
else
    echo "❌ 主网关启动失败"
    tail -20 logs/error.log
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ ClawsJoy v5.0.0 启动完成"
echo "=========================================="
echo "API: http://localhost:$PORT"
echo "健康检查: http://localhost:$PORT/api/health"
echo "私人管家: http://localhost:$PORT/api/butler/chat"
echo ""
echo "停止服务: ./stop_all.sh"
