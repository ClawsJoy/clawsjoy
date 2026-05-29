#!/bin/bash
AGENT="$1"
shift
MESSAGE="$*"

# 调用 Agent 获取指令
openclaw agent --agent "$AGENT" -m "$MESSAGE" --session-id "task_$(date +%s)" | \
    ~/clawsjoy/bin/task_listener.sh "$AGENT" "$MESSAGE"
