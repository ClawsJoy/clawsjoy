#!/bin/bash
# 高质量视频工作流

echo "=== 香港内容工作流 v3（高质量）==="

# Step 1: 规划话题
TOPIC=$(python3 skills/topic_planner/execute.py '{"category": "immigration"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['topics'][0])")
echo "今日话题: $TOPIC"

# Step 2: 生成脚本
python3 skills/content_writer/execute.py "{\"topic\": \"$TOPIC\", \"duration\": 3}" > /tmp/script.json
SCRIPT=$(cat /tmp/script.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('script', ''))")
echo "脚本已生成"

# Step 3: 制作高质量视频
curl -s -X POST http://localhost:8105/api/promo/make \
  -H "Content-Type: application/json" \
  -d "{\"city\": \"香港\", \"style\": \"人文\", \"topic\": \"$TOPIC\", \"script\": \"$SCRIPT\"}" \
  > /tmp/video_result.json

VIDEO_URL=$(cat /tmp/video_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('video_url', ''))")
THUMBNAIL_URL=$(cat /tmp/video_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('thumbnail_url', ''))")
IMAGE_COUNT=$(cat /tmp/video_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('image_count', 0))")
HAS_NARRATION=$(cat /tmp/video_result.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('has_narration', False))")

echo ""
echo "✅ 视频生成完成！"
echo "   视频: http://localhost:8082$VIDEO_URL"
echo "   封面: http://localhost:8082$THUMBNAIL_URL"
echo "   图片数: $IMAGE_COUNT 张"
echo "   配音: $([ "$HAS_NARRATION" = "True" ] && echo "有" || echo "无")"
