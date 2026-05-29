# ClawsJoy API 参考

## 认证服务 (5444)

### POST /auth/login
登录获取 token

```json
请求: {"user_id": "user1", "password": "admin123"}
响应: {"success": true, "token": "...", "user": {...}}
GET /auth/verify
验证 token
请求头: Authorization: Bearer <token>
响应: {"valid": true, "user": {...}}
驱动服务 (5443)
GET /api/driver/config/desensitization
获取脱敏配置

GET /health
健康检查

偏好服务 (5445)
POST /preference/save
保存用户偏好

GET /preference/load
加载用户偏好

Web 服务 (5446)
GET /
Web 界面

POST /api/secure/chat
安全对话

GET /api/secure/status
获取用户状态

POST /api/heartbeat/{agent_name}
Agent 心跳
