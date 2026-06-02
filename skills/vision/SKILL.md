---
name: vision
description: 图像识别技能，使用 moondream 模型识别图片内容
category: image
version: 1.0.0
author: ClawsJoy
use_when: 需要识别图片内容、描述图片、分析图像
not_for: 视频处理、音频处理
---

# Vision Skill

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| image_path | string | 是 | 图片文件路径 |
| prompt | string | 否 | 识别提示词，默认为"描述这张图片" |

## 返回值
| 字段 | 类型 | 描述 |
|------|------|------|
| success | boolean | 是否成功 |
| result | string | 图像描述 |
| image | string | 图片路径 |
