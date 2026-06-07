---
name: 3d_render
description: 3D 渲染与建模技能，支持 Blender 场景渲染、模型转换
category: 3d
version: 1.0.0
author: ClawsJoy
use_when: 需要渲染3D场景、生成3D模型、转换模型格式
not_for: 2D图像处理
---

# 3D Render Skill

## 功能
- 渲染 3D 场景（立方体、球体、圆柱体）
- 转换 3D 模型格式
- Blender 集成

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| action | string | 是 | render/convert |
| shape | string | 否 | cube/sphere/cylinder |
