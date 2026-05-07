---
name: clawsjoy-tenant
description: 租户管理（创建、查询、配置）
version: 1.0.0
parameters:
  - name: action
    type: string
    required: true
    enum: [list, create, delete, stats]
  - name: tenant_id
    type: string
    required: false
  - name: name
    type: string
    required: false
---

# 租户管理 Skill

## 使用示例

### 列出租户
```python
execute_skill("clawsjoy-tenant", {"action": "list"})
```

### 创建租户
```python
execute_skill("clawsjoy-tenant", {"action": "create", "name": "新租户"})
```

### 删除租户
```python
execute_skill("clawsjoy-tenant", {"action": "delete", "tenant_id": "xxx"})
```

### 租户统计
```python
execute_skill("clawsjoy-tenant", {"action": "stats", "tenant_id": "xxx"})
```