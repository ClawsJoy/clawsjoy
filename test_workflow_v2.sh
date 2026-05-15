#!/bin/bash

echo "=== 香港内容工作流 v2 ==="

# Step 1: 规划话题
TOPIC=$(python3 skills/topic_planner/execute.py '{"category": "immigration"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['topics'][0])")
echo "今日话题: $TOPIC"

# Step 2: 生成脚本
python3 skills/content_writer/execute.py "{\"topic\": \"$TOPIC\", \"duration\": 3}" > /tmp/script.json
SCRIPT=$(cat /tmp/script.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('script', ''))")
echo "脚本已生成"

# Step 3: 制作视频 - 把话题也传进去！
# 注意：需要修改 promo skill 支持 topic 参数
curl -s -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d "{\"city\": \"香港\", \"style\": \"人文\", \"topic\": \"$TOPIC\", \"script\": \"$SCRIPT\"}" \
  > /tmp/video_result.json

VIDEO_URL=$(cat /tmp/video_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('video_url', ''))")
echo "视频已生成: $VIDEO_URL"

echo "✅ 完成"
