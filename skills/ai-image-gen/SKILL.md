---
name: ai-image-gen
description: AI 图像生成技能，使用 Stable Diffusion 生成高质量图像
category: image
version: 1.1.0
author: ClawsJoy
security_grade: 🟢 A
use_when: 需要生成图像、画图、AI绘画、图片创作
not_for: 图像编辑、视频生成
---

# AI Image Generator

## When to Run
- 用户请求生成图像
- 用户说"画一张..."、"生成图片"、"AI绘画"

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| prompt | string | 是 | 图像描述提示词 |
| negative_prompt | string | 否 | 负面提示词 |
| width | int | 否 | 图像宽度，默认512 |
| height | int | 否 | 图像高度，默认512 |
| steps | int | 否 | 推理步数，默认20 |

## 返回值
| 字段 | 类型 | 描述 |
|------|------|------|
| success | boolean | 是否成功 |
| image_url | string | 生成的图片URL |
| image_path | string | 本地图片路径 |
