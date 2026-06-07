---
name: video-trim
description: 视频裁剪，截取指定时间段的视频
version: 1.0.0
author: ClawsJoy
use_when: 需要裁剪视频、截取片段
---

# 视频裁剪技能

## 参数
| 参数 | 类型 | 描述 |
|------|------|------|
| video_path | string | 视频文件路径 |
| start | string | 开始时间 (HH:MM:SS 或 MM:SS) |
| end | string | 结束时间 |
| duration | string | 持续时间 |

## 示例
- "裁剪 00:10 到 00:20"
- "截取 10秒到30秒"
