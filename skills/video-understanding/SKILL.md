---
name: video-understanding
description: 视频理解 - 提取视频中的多模态信息
version: 1.0.0
author: ClawsJoy
use_when: 需要分析视频内容、提取视频信息、视频理解
not_for: 视频下载、视频编辑
---

# 视频理解技能

提取视频中的多模态信息，供 Agent 交流使用。

## 输入参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| video_path | string | 是 | 本地视频文件路径 |
| extract_subs | boolean | 否 | 是否提取字幕（默认 true）|
| extract_frames | boolean | 否 | 是否提取关键帧（默认 false）|

## 输出格式
```json
{
  "success": true,
  "metadata": {...},
  "transcription": "...",
  "summary": "...",
  "topics": [...]
}
