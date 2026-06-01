#!/bin/bash
# 加载环境变量
if [ -f config/.env ]; then
    export $(cat config/.env | grep -v "^#" | xargs)
fi

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

# 停止旧服务
pkill -f gunicorn 2>/dev/null
sleep 2

# 启动新服务 (使用配置文件)
nohup gunicorn -c gunicorn.conf.py agent_gateway_enhanced:app > logs/gunicorn.log 2>&1 &

sleep 3

# 检查状态
if pgrep -f "gunicorn" > /dev/null; then
    echo "✅ ClawsJoy v5 生产环境已启动"
    echo "   网关: http://localhost:5002"
    echo "   Workers: 4, Threads: 8, 并发: 32"
else
    echo "❌ 启动失败，查看日志: tail -50 logs/gunicorn.log"
fi
