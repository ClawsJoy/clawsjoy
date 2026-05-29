# ClawsJoy 4.0 管理员指南

## 服务管理

### 启动所有服务
```bash
cd /mnt/d/clawsjoy_clean
python3 auth_service.py &
python3 driver_service_https.py &
python3 user_preference_service.py &
python3 web_dashboard_secure.py &

停止服务
pkill -f "auth_service|driver_service|user_preference|web_dashboard_secure"

查看日志
tail -f logs/auth.log
tail -f logs/driver.log
配置管理
脱敏规则
编辑 config/driver/desensitization.yaml

用户管理
编辑 auth_service.py 中的 USERS 字典

监控
健康检查: https://localhost:5443/health

认证验证: https://localhost:5444/auth/verify

