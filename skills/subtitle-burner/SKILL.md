---
name: subtitle_burner
version: 1.0.0
description: 'TTS配音+字幕生成+嵌入视频，一键完成'
author: ClawsJoy
security_grade: 🟢 A
use_when: 字幕, 配音合成, 视频字幕
not_for: 视频剪辑
---

# subtitle_burner

## When to Run
- 用户需要给视频配上对白配音和字幕

## Workflow
1. EdgeTTS生成音频
2. ffprobe获取时长
3. 按标点分段生成SRT字幕
4. ffmpeg嵌入视频

## Changelog
### v1.0.0 (2026-06-26)
- 初始版本
