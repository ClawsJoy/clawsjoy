---
name: video-qa
description: 针对视频内容进行问答，理解视频画面
version: 1.0.0
author: ClawsJoy
use_when: 需要询问视频内容、理解视频画面
not_for: 视频下载、视频编辑
triggers:
  - 视频里有什么
  - 这个视频在讲什么
  - 视频里的人在做什么
  - 视频中出现了什么
---

# 视频问答技能

针对视频内容进行自然语言问答。

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| video_path | string | 是 | 视频文件路径 |
| question | string | 是 | 关于视频的问题 |
| model | string | 否 | 视觉模型（fast/accurate）|
