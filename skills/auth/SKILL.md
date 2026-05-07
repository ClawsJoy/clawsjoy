---
name: clawsjoy-auth
description: 用户认证与登录管理
version: 1.0.0
parameters:
  - name: action
    type: string
    required: true
    enum: [login, register, health]
  - name: username
    type: string
    required: false
  - name: password
    type: string
    required: false
---

# 认证 Skill

## 使用示例

### 登录
```python
execute_skill("clawsjoy-auth", {"action": "login", "username": "admin", "password": "admin123"})
```

### 注册
```python
execute_skill("clawsjoy-auth", {"action": "register", "username": "newuser", "password": "pass123"})
```

### 健康检查
```python
execute_skill("clawsjoy-auth", {"action": "health"})
```
