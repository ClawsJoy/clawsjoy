#!/bin/bash
# GPU 任务提交器

TASK_TYPE="$1"

case $TASK_TYPE in
    video)
        echo "提交视频合成任务..."
        curl -s -X POST http://localhost:8105/api/promo/make \
            -H "Content-Type: application/json" \
            -d '{"topic":"香港优才计划"}' &
        ;;
    image)
        echo "提交 AI 生图任务..."
        # python3 skills/sd_image_gen.py "Hong Kong skyline" &
        echo "AI 生图功能待配置"
        ;;
    status)
        echo "=== GPU 任务状态 ==="
        pgrep -af "ffmpeg|promo_api" && echo "GPU 忙碌" || echo "GPU 空闲"
        ;;
    *)
        echo "用法: $0 {video|image|status}"
        ;;
esac
