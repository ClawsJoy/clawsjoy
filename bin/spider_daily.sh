#!/bin/bash
# Spider 每日定时采集

LOG_FILE="$HOME/clawsjoy/logs/spider_daily.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Spider 每日采集开始" >> "$LOG_FILE"

# 每日采集主题
TOPICS=(
    "hongkong skyline"
    "victoria harbour" 
    "hongkong street"
    "artificial intelligence"
    "robot future"
    "technology circuit"
)

for topic in "${TOPICS[@]}"; do
    echo "采集: $topic" >> "$LOG_FILE"
    ~/clawsjoy/bin/spider_unsplash "$topic" 3 >> "$LOG_FILE" 2>&1
    sleep 2
done

echo "[$DATE] Spider 每日采集完成" >> "$LOG_FILE"
echo "✅ 采集完成，素材已更新"
