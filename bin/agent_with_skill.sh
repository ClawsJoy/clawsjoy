#!/bin/bash
TENANT_ID="${1:-1}"
shift
QUERY="$@"

# 1. 检索记忆
MEMORY=$(python3 ~/clawsjoy/bin/memory_retriever.py retrieve "$TENANT_ID" "$QUERY" 2>/dev/null)

# 2. 检索 Skills
SKILLS=$(ls ~/clawsjoy/skills/auto_generated/*.md 2>/dev/null | head -3)
SKILL_LIST=""
for s in $SKILLS; do
    SKILL_LIST="$SKILL_LIST\n- $(basename "$s" .md)"
done

# 3. 构建 Prompt
PROMPT="${MEMORY}

## 可用 Skills
$SKILL_LIST

用户问题: ${QUERY}"

# 4. 调用
openclaw infer model run --model ollama/qwen2.5:3b --prompt "$PROMPT"
