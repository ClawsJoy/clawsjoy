#!/bin/bash
# 生产环境部署脚本

set -e

echo "🚀 开始部署 ClawsJoy v6.0"

# 1. 拉取最新代码
git pull origin dev

# 2. 构建镜像
docker build -f Dockerfile.prod -t clawsjoy/gateway:latest .

# 3. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 等待服务就绪
sleep 10

# 5. 健康检查
curl -f http://localhost:5002/health || exit 1

# 6. 查看日志
docker-compose -f docker-compose.prod.yml logs --tail=50

echo "✅ 部署完成"
