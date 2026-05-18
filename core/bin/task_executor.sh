#!/bin/bash
# 任务执行器：接收任务描述，调用 Agent 拆解并执行

TASK="$1"

if [ -z "$TASK" ]; then
    echo "用法: task_executor.sh <任务描述>"
    exit 1
fi

echo "🎯 任务: $TASK"
echo "🤖 调用 Agent 拆解..."

# 调用 Agent 获取命令
CMD=$(openclaw agent --agent main -m "把以下任务转换成可执行的bash命令，只输出命令，不要解释。任务: $TASK" --session-id "task_$(date +%s)" 2>/dev/null)

echo "📋 执行: $CMD"
eval "$CMD"
