#!/bin/bash
# 专门修复视频任务

log() { echo "[$(date)] $1"; }

log "🎬 开始修复视频任务..."

# 重新提交正确的宣传片
~/clawsjoy/bin/write_video "ClawsJoy 公司宣传片 V3 (修复版)" "ClawsJoy 官方宣传片 - 让AI安全地为每个人工作。时长45秒，主题：多租户隔离、Agent自动进化、文件事件驱动。YouTube演示: https://www.youtube.com/watch?v=dQw4w9WgXcQ" "video-maker"

log "✅ 已重新提交宣传片 V3"

# 重新提交品牌宣传片
~/clawsjoy/bin/write_video "ClawsJoy 品牌宣传片 - 第17期" "ClawsJoy 每周宣传片 - 主题：Agent自动进化：越用越聪明。内容：Writer内容创作、Designer设计生成、Reviewer智能审核、Messenger多平台发布。时长45秒" "video-maker"

log "✅ 已重新提交品牌宣传片"

log "🎬 视频任务修复完成"
