---
name: clawsjoy-promo
description: 制作城市宣传片
version: 1.0.0
parameters:
  - name: city
    type: string
    required: true
  - name: style
    type: string
    required: false
    default: "科技"
---

# 宣传片制作 Skill

## 使用示例
```python
execute_skill("clawsjoy-promo", {"city": "香港", "style": "科技"})
```