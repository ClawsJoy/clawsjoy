#!/bin/bash
TENANT_ID="${1:-1}"
QUERY="$2"

if [ -z "$QUERY" ]; then
    echo "用法: memory_search.sh <tenant_id> <query>"
    exit 1
fi

# 先尝试关键词检索
echo "🔍 关键词检索..."
KEYWORD_RESULT=$(python3 ~/clawsjoy/bin/memory_retriever.py retrieve "$TENANT_ID" "$QUERY" 2>/dev/null)

if [ -n "$KEYWORD_RESULT" ] && [ ${#KEYWORD_RESULT} -gt 50 ]; then
    echo "$KEYWORD_RESULT"
else
    echo "📊 关键词结果较少，启用向量检索..."
    source ~/clawsjoy/venv/bin/activate
    python3 ~/clawsjoy/bin/memory_retriever_v2.py retrieve "$TENANT_ID" "$QUERY"
    deactivate
fi
