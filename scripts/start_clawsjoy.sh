#!/bin/bash
cd /home/flybo/clawsjoy_clean
export PATH=/home/flybo/miniconda3/bin:$PATH
export DEFAULT_LLM_MODEL=qwen2.5:3b
export OLLAMA_ENDPOINT=http://127.0.0.1
export OLLAMA_PORT=11434

# 启动 Clawsjoy 的 Web 服务
nohup python web_dashboard.py > logs/web.log 2>&1 &

echo "Clawsjoy Web 服务已启动"
echo "访问 http://localhost:5000"
