---
name: ai-image-gen
version: 1.1.0
description: >
  AI 图像生成技能
  Use when: 需要生成角色图像、场景图像
  NOT for: 视频生成、图像编辑
author: ClawsJoy
security_grade: 🟢 A
---

# AI Image Generator

## When to Run
- 用户请求生成图像
- 创建角色形象
- 生成场景图片

## Workflow
1. 解析提示词
2. 保存提示词到文件
3. 等待真实AI模型生成

## Output Format
```json
{
  "success": true,
  "result": {
    "prompt_file": "/path/to/prompt.txt",
    "prompt": "原始提示词"
  }
}
Changelog
v1.1.0 (2026-05-17)
独立模式，无外部依赖

保存提示词供后续生成
