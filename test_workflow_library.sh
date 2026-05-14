#!/bin/bash
# 使用内容库的视频工作流

cd /mnt/d/clawsjoy

# 随机获取一个话题和脚本
RESULT=$(python3 skills/assemble_from_library.py)
TOPIC=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('topic', ''))")
SCRIPT=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin).get('script', ''))")

echo "📌 话题: $TOPIC"
echo "📝 脚本长度: ${#SCRIPT} 字符"

# 制作视频
curl -s -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d "{\"city\":\"香港\",\"style\":\"人文\",\"topic\":\"$TOPIC\",\"script\":\"$SCRIPT\"}" \
  | python3 -m json.tool

echo ""
echo "🎬 视频已生成"
