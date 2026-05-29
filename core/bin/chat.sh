#!/bin/bash
# 直接调用 Ollama 的聊天脚本

QUERY="$*"
if [ -z "$QUERY" ]; then
    echo "用法: chat.sh <你的问题>"
    exit 1
fi

curl -s http://localhost:11434/api/generate -d "{
    \"model\": \"qwen2.5:3b\",
    \"prompt\": \"$QUERY\",
    \"stream\": false
}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('response', ''))"
