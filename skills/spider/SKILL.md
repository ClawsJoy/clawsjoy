---
name: clawsjoy-spider
description: 从 Unsplash 采集图片
version: 1.0.0
parameters:
  - name: keyword
    type: string
    required: true
  - name: count
    type: integer
    required: false
    default: 5
---

# 图片采集 Skill

## 使用示例
```python
execute_skill("clawsjoy-spider", {"keyword": "香港夜景", "count": 5})
```