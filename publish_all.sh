#!/bin/bash
# 批量发布所有未发布的视频

cd /mnt/d/clawsjoy/web/videos

for video in 香港_*.mp4; do
    if [ ! -f "published_${video}.txt" ]; then
        echo "📤 发布: $video"
        # TODO: 调用 YouTube API
        # 标记已发布
        touch "published_${video}.txt"
        sleep 2
    fi
done
