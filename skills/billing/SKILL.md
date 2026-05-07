---
name: clawsjoy-billing
description: 租户计费与余额管理
version: 1.0.0
parameters:
  - name: action
    type: string
    required: true
    enum: [balance, record, recharge]
  - name: tenant_id
    type: string
    required: true
  - name: amount
    type: number
    required: false
---

# 计费 Skill

## 使用示例

### 查询余额
```python
execute_skill("clawsjoy-billing", {"action": "balance", "tenant_id": "1"})
```

### 记录消费
```python
execute_skill("clawsjoy-billing", {"action": "record", "tenant_id": "1", "amount": 10})
```

### 充值
```python
execute_skill("clawsjoy-billing", {"action": "recharge", "tenant_id": "1", "amount": 100})
```