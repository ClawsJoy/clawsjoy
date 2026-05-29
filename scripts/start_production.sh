#!/bin/bash
# ClawsJoy 生产级启动脚本

cd /home/flybo/clawsjoy_clean

# 设置环境变量
export PYTHONPATH=/home/flybo/clawsjoy_clean
export OLLAMA_URL=http://localhost:11434

# 停止旧进程
pkill -9 -f "gunicorn.*agent_gateway" 2>/dev/null
sleep 2

# 启动旧版增强服务 (4 workers, gevent)
echo "🚀 启动旧版增强服务 (生产模式)..."
gunicorn -w 4 -k gevent \
    --bind 0.0.0.0:5002 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    agent_gateway_enhanced:app &

sleep 3

# 启动 v5.0 测试服务 (2 workers)
echo "🚀 启动 v5.0 测试服务..."
gunicorn -w 2 -k gevent \
    --bind 0.0.0.0:5003 \
    --timeout 120 \
    agent_gateway_v5_complete_fixed:app &

sleep 3

echo ""
echo "✅ 生产服务已启动"
echo "   旧版: http://localhost:5002 (4 workers)"
echo "   v5.0: http://localhost:5003 (2 workers)"
echo ""
echo "监控命令:"
echo "   watch -n 1 'ps aux | grep gunicorn | grep -v grep'"
