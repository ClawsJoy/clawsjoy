#!/bin/bash
# 从视频生成封面图

VIDEO_FILE="$1"
THUMBNAIL_FILE="${VIDEO_FILE%.mp4}.jpg"

if [ ! -f "$VIDEO_FILE" ]; then
    echo "视频文件不存在: $VIDEO_FILE"
    exit 1
fi

# 提取第1秒的画面
ffmpeg -i "$VIDEO_FILE" -ss 00:00:01 -vframes 1 -q:v 2 "$THUMBNAIL_FILE" -y 2>/dev/null

if [ -f "$THUMBNAIL_FILE" ]; then
    echo "✅ 封面已生成: $THUMBNAIL_FILE"
    
    # 添加文字（可选）
    # convert "$THUMBNAIL_FILE" -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf -pointsize 30 -fill white -annotate +50+50 "香港" "$THUMBNAIL_FILE"
else
    echo "❌ 封面生成失败"
fi
