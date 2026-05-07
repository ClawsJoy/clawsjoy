#!/bin/bash
# 稳定版工作流（不依赖 AI 生成脚本）

echo "=== 稳定版视频工作流 ==="

# 话题列表
TOPICS=(
    "香港优才计划2026最新政策"
    "香港高才通申请攻略"
    "香港留学一年费用"
    "香港身份转永居条件"
)

# 随机选一个话题
RANDOM_TOPIC=${TOPICS[$RANDOM % ${#TOPICS[@]}]}
echo "📌 今日话题: $RANDOM_TOPIC"

# 使用固定模板生成脚本
SCRIPT="香港${RANDOM_TOPIC}！三大重点：第一政策有变化门槛降低，第二申请更简单流程优化，第三获批更快3-6个月出结果。建议分数够就赶紧递交！点赞关注下期见。"

echo "📝 脚本: $SCRIPT"

# 制作视频
curl -s -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d "{\"city\":\"香港\",\"style\":\"人文\",\"topic\":\"$RANDOM_TOPIC\",\"script\":\"$SCRIPT\"}" \
  | python3 -m json.tool

echo ""
echo "✅ 完成"
