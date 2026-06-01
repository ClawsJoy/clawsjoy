#!/bin/bash
# 每日自动任务脚本

cd /mnt/d/clawsjoy

# 话题池
TOPICS=(
    "香港优才计划2026最新政策"
    "香港高才通申请攻略"
    "香港留学一年费用"
    "香港身份转永居条件"
    "香港大学2025本科申请"
)

# 随机选一个话题
RANDOM_TOPIC=${TOPICS[$RANDOM % ${#TOPICS[@]}]}

echo "$(date): 开始处理 - $RANDOM_TOPIC"

# 调用 Promo API 制作视频
curl -s -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d "{\"city\":\"香港\",\"style\":\"人文\"}" \
  > /tmp/video_result.json

# 记录日志
echo "$(date): 视频已生成" >> logs/daily.log

echo "✅ 完成: $RANDOM_TOPIC"
