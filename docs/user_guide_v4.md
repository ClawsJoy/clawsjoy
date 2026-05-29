# ClawsJoy 4.0 用户指南

## 快速开始

### 登录
POST https://localhost:5444/auth/login
{"user_id": "user1", "password": "admin123"}

### 对话
POST https://localhost:5446/api/secure/chat
{"message": "生成一张图片"}

### 保存偏好
POST https://localhost:5445/preference/save
{"category": "image", "preferences": {"style": "写实"}}


## 可用用户

| 用户 | 密码 | 角色 |
|------|------|------|
| user1 | admin123 | 管理员 |
| user2 | user123 | 普通用户 |
| user3 | user123 | 普通用户 |

