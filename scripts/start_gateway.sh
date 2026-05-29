#!/bin/bash
# ClawsJoy 网关自动启动脚本

cd /home/flybo/clawsjoy_clean
export PYTHONPATH=/home/flybo/clawsjoy_clean:$PYTHONPATH

# 检查是否已经在运行
if pgrep -f "gunicorn.*5002" > /dev/null; then
    echo "网关已在运行"
    exit 0
fi

# 启动 Ollama（如果未运行）
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "启动 Ollama..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi

# 启动网关
echo "启动网关..."
nohup /home/flybo/miniconda3/bin/gunicorn -w 2 -k gevent --bind 0.0.0.0:5002 --timeout 120 agent_gateway_enhanced:app --daemon > /tmp/gateway.log 2>&1 &

sleep 2
echo "网关已启动"
