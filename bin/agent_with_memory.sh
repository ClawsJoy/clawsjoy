#!/bin/bash
# 带记忆检索的 Agent 调用
# 用法: agent_with_memory.sh <tenant_id> <query>

TENANT_ID="${1:-1}"
shift
QUERY="$@"

if [ -z "$QUERY" ]; then
    echo "用法: agent_with_memory.sh <tenant_id> <query>"
    echo "示例: agent_with_memory.sh 1 帮我制作香港宣传片"
    exit 1
fi

echo "🔍 租户 $TENANT_ID: 检索相关记忆..."
MEMORY=$(python3 ~/clawsjoy/bin/memory_retriever.py "$TENANT_ID" "$QUERY" 2>/dev/null)

if [ -n "$MEMORY" ]; then
    echo "📚 找到相关历史经验，已注入上下文..."
    PROMPT="${MEMORY}

用户问题: ${QUERY}

请参考以上历史经验回答。"
else
    echo "📚 未找到相关历史记忆，使用通用回答..."
    PROMPT="${QUERY}"
fi

echo "🤖 调用 Agent..."
openclaw agent --agent main -m "$PROMPT"
