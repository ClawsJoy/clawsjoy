#!/bin/bash
echo "🔧 ClawsJoy 快速修复"

# 1. 备份当前配置
cp .env .env.backup

# 2. 生成新密钥
NEW_JWT=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "JWT_SECRET=$NEW_JWT" >> .env

# 3. 修复权限
chmod 600 .env
chmod 750 scripts/

# 4. 清理缓存
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 5. 重启服务
pkill -f gunicorn
sleep 2
nohup gunicorn -c gunicorn.conf.py agent_gateway_enhanced:app &

echo "✅ 修复完成，请测试: curl http://localhost:5002/health"
