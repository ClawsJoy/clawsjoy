#!/bin/bash
# 流水线执行器：调用 main 获取任务列表，然后顺序执行

MAIN_TASK="$1"

echo "🎯 主任务: $MAIN_TASK"
echo "📋 获取任务列表..."

# 调用 main 获取任务列表
TASKS=$(openclaw agent --agent main -m "$MAIN_TASK" --session-id "pipe_$(date +%s)" 2>/dev/null | grep "TASK|")

if [ -z "$TASKS" ]; then
    echo "❌ main 未返回任务列表"
    exit 1
fi

echo "$TASKS" | while read line; do
    AGENT=$(echo "$line" | cut -d'|' -f2)
    DESC=$(echo "$line" | cut -d'|' -f3-)
    
    echo ""
    echo "🚀 执行: $AGENT - $DESC"
    ~/clawsjoy/bin/agent_do.sh "$AGENT" "$DESC"
    
    echo "⏳ 等待完成..."
    sleep 3
done

echo ""
echo "✅ 流水线执行完成"
