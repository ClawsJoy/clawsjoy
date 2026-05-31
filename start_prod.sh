#!/bin/bash
# ClawsJoy v5 生产环境启动脚本

cd /home/flybo/clawsjoy_v5

# 设置环境变量
export PYTHONPATH=/home/flybo/clawsjoy_v5:$PYTHONPATH
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434

# 启动 Redis（如果未运行）
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes
    echo "✅ Redis 已启动"
fi

# 启动 Ollama（如果未运行）
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
    echo "✅ Ollama 已启动"
fi

# 启动 LLM 服务
pkill -f llm_service 2>/dev/null
nohup python3 scripts/llm_service.py > logs/llm_service.log 2>&1 &
echo "✅ LLM 服务已启动"

# 使用 Gunicorn 启动网关
pkill -f gunicorn 2>/dev/null
gunicorn -w 4 --threads 8 --worker-class gthread \
    --bind 0.0.0.0:5002 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    agent_gateway_enhanced:app

echo "✅ ClawsJoy v5 生产环境已启动"
echo "   网关: http://localhost:5002"
echo "   Workers: 4, Threads: 8, 并发: 32"
