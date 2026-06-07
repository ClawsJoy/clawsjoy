---
name: video-analyze
description: 分析本地视频文件，提取基本信息（时长、分辨率、大小等）
category: video
version: 1.0.0
author: ClawsJoy
use_when: 需要分析本地视频文件、查看视频信息
not_for: 在线视频下载
---

# 视频分析技能

分析本地视频文件，使用 ffprobe 提取视频元数据。

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| video_path | string | 是 | 视频文件路径 |

## 返回值
- duration: 时长（秒）
- resolution: 分辨率
- size_mb: 文件大小
- codec: 编码格式
