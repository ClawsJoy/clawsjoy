#!/bin/bash
# 每日内容生产 - 香港系列

DATE=$(date +%Y%m%d)
LOG_FILE="logs/daily_$DATE.log"

mkdir -p logs

echo "=== 每日内容生产: $(date) ===" | tee -a "$LOG_FILE"

# 从话题池中随机选一个话题
TOPIC=$(shuf -n 1 topics.txt)
echo "今日话题: $TOPIC" | tee -a "$LOG_FILE"

# 生成脚本
echo "[1/2] 生成脚本..." | tee -a "$LOG_FILE"
./clawsjoy.sh write --topic "$TOPIC" >> "$LOG_FILE" 2>&1

# 制作视频
echo "[2/2] 制作视频..." | tee -a "$LOG_FILE"
./clawsjoy.sh make --city "香港" --style "人文" >> "$LOG_FILE" 2>&1

echo "✅ 完成: $(date)" | tee -a "$LOG_FILE"
