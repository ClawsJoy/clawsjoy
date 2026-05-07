#!/bin/bash
echo "=== 测试香港内容工作流 ==="

# Step 1: 规划话题
echo ""
echo "1️⃣ 规划话题..."
TOPIC=$(python3 skills/topic_planner/execute.py '{"category": "immigration"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['topics'][0])")
echo "今日话题: $TOPIC"

# Step 2: 生成脚本
echo ""
echo "2️⃣ 生成脚本..."
python3 skills/content_writer/execute.py "{\"topic\": \"$TOPIC\", \"duration\": 3}" > /tmp/script.json
SCRIPT=$(cat /tmp/script.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('script', '')[:200])")
echo "脚本预览: $SCRIPT..."

# Step 3: 制作视频
echo ""
echo "3️⃣ 制作视频..."
python3 skills/promo/execute.py '{"city": "香港", "style": "人文"}'

echo ""
echo "✅ 工作流测试完成"
