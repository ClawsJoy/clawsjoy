---
name: auto_generated
description: auto_generated 技能
category: general
version: 1.0.0
tags: [auto_generated]
---

# auto_generated

## 功能描述
auto_generated 技能

## 参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params | dict | 是 | 技能参数 |

## 示例
```python
execute({
    "skill": "auto_generated",
    "params": {}
})

## auto_vision_combo

自动组合技能: vision → translate

**组合技能:** vision, translate

**参数传递规则:**

- vision: 需要 `image_path` 参数
- translate: 需要 `text` 参数，会自动从前置技能结果提取