#!/bin/bash
# 批量处理话题：生成脚本 → 制作视频

TOPICS_FILE="topics.txt"
OUTPUT_DIR="output"

mkdir -p "$OUTPUT_DIR"/{scripts,videos}

echo "=== 批量处理开始 ==="
cat "$TOPICS_FILE" | while IFS= read -r topic; do
    echo ""
    echo "📌 处理话题: $topic"
    
    # 生成脚本
    echo "   → 生成脚本..."
    ./clawsjoy.sh write --topic "$topic"
    
    # 制作视频（每处理5个休息一下）
    echo "   → 制作视频..."
    ./clawsjoy.sh make --city "香港" --style "人文"
    
    # 避免请求过快
    sleep 2
done
echo ""
echo "=== 批量处理完成 ==="
