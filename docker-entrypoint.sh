#!/bin/bash
set -e

echo "🚀 ClawsJoy 启动中..."

# 启动 Ollama（如果需要）
if [ -n "$OLLAMA_ENABLED" ]; then
    ollama serve &
    sleep 5
    ollama pull qwen2.5:7b
fi

# 启动各个服务
python3 agent_gateway_web.py &
python3 file_service_complete.py &
python3 multi_agent_service_v2.py &
python3 doc_generator.py &
python3 agent_api.py &
python3 web_server.py &

# 等待所有后台进程
wait
