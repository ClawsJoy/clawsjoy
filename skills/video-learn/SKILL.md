---
name: video-learn
description: 自学习视频处理 - 根据自然语言反馈自动调整参数
version: 1.0.0
author: ClawsJoy
use_when: 用户对视频效果不满意，需要自动调整
not_for: 简单视频下载
---

# 自学习视频处理

根据自然语言反馈，自动调整视频处理参数。

## 输入
- video_path: 视频路径
- feedback: 用户反馈（自然语言）

## 输出
- adjusted_video: 调整后的视频
- changes: 应用的参数调整
- learning: 学习记录
