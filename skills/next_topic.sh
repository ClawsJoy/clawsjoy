#!/bin/bash
# 每天取下一个话题，不重复

QUEUE_FILE="topics_queue.txt"
HISTORY_FILE="output/history/topics_done.txt"

# 获取下一个未使用的话题
while read topic; do
    if ! grep -qF "$topic" "$HISTORY_FILE" 2>/dev/null; then
        echo "$topic"
        echo "$(date): $topic" >> "$HISTORY_FILE"
        break
    fi
done < "$QUEUE_FILE"

# 如果所有话题都用完了，重置历史
if [ -z "$TOPIC" ]; then
    echo "⚠️ 所有话题已用完，重置" >> "$HISTORY_FILE"
    rm -f "$HISTORY_FILE"
    head -1 "$QUEUE_FILE"
fi
