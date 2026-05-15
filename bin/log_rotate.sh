#!/bin/bash
# 日志轮转 - 保留最近7天，单个文件不超过50MB

LOG_DIR="/mnt/d/clawsjoy/logs"
MAX_SIZE=50  # MB
KEEP_DAYS=7

for log in "$LOG_DIR"/*.log; do
    if [ -f "$log" ]; then
        size=$(du -m "$log" | cut -f1)
        if [ "$size" -gt "$MAX_SIZE" ]; then
            mv "$log" "${log}.old"
            echo "$(date): 日志轮转 $log (${size}MB)" >> "$LOG_DIR/rotate.log"
        fi
    fi
done

# 删除7天前的日志
find "$LOG_DIR" -name "*.log.*" -mtime +$KEEP_DAYS -delete
find "$LOG_DIR" -name "*.old" -mtime +$KEEP_DAYS -delete

echo "$(date): 日志轮转完成" >> "$LOG_DIR/rotate.log"
