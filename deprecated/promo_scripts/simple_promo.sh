#!/bin/bash
CITY=$1
IMG_DIR="/home/flybo/clawsjoy/web/images/$CITY"
OUTPUT="/home/flybo/clawsjoy/web/videos/${CITY}_promo_$(date +%s).mp4"

# 生成视频
ffmpeg -y -loop 1 -i "$IMG_DIR"/*.jpg -c:v libx264 -t 15 -pix_fmt yuv420p -vf "scale=1920:1080" "$OUTPUT" 2>/dev/null

echo "{\"success\": true, \"video_url\": \"/videos/$(basename $OUTPUT)\"}"
