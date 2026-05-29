---
name: image
version: 1.0.0
description: '图像处理技能，包括图像识别、图片分析'
author: ClawsJoy
security_grade: 🟢 A
use_when: 图像处理、图片识别、图片描述
not_for: 视频处理、音频处理
---

# Image Skill

## 子技能
| 技能名 | 描述 |
|--------|------|
| vision | 图像识别，使用 llava:7b 模型 |

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| image_path | string | 是 | 图片文件路径 |
| prompt | string | 否 | 识别提示词 |

## 示例
```json
{
  "skill": "vision",
  "params": {
    "image_path": "/tmp/photo.jpg"
  }
}
