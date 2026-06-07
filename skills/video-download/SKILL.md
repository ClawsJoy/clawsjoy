---
name: video_download
version: 1.0.0
description: '下载 YouTube 视频到本地'
author: ClawsJoy
security_grade: 🟢 A
use_when: 下载视频, 保存视频, youtube下载
not_for: 下载其他平台视频
---

# 视频下载技能

## When to Run
- 用户请求下载 YouTube 视频
- 用户提供 YouTube 链接要求保存

## Workflow
1. 获取 YouTube URL
2. 使用 yt-dlp 下载视频
3. 返回下载结果

## Changelog
### v1.0.0 (2026-06-06)
- 创建视频下载技能
