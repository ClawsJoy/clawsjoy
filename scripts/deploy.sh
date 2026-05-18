#!/bin/bash
# ClawsJoy 4.0 生产部署脚本

set -e

echo "=========================================="
echo "ClawsJoy 4.0 生产部署"
echo "=========================================="

# 1. 停止旧服务
echo "1. 停止旧服务..."
./stop_all.sh 2>/dev/null || true

# 2. 备份当前数据
echo "2. 备份数据..."
BACKUP_DIR="/mnt/d/clawsjoy-backups/deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r data "$BACKUP_DIR/" 2>/dev/null || true
cp -r memory "$BACKUP_DIR/" 2>/dev/null || true
cp -r config "$BACKUP_DIR/" 2>/dev/null || true
echo "   备份到: $BACKUP_DIR"

# 3. 更新代码
echo "3. 更新代码..."
git pull origin main 2>/dev/null || echo "   跳过 git pull"

# 4. 安装依赖
echo "4. 安装依赖..."
pip install -r requirements.txt -q

# 5. 启动服务
echo "5. 启动服务..."
./start_all.sh

# 6. 等待服务就绪
echo "6. 等待服务就绪..."
sleep 5

# 7. 健康检查
echo "7. 健康检查..."
for i in 1 2 3 4 5; do
    if curl -k -s https://localhost:5446/api/health | grep -q "healthy"; then
        echo "   ✅ 服务健康"
        break
    fi
    echo "   等待中... ($i/5)"
    sleep 3
done

# 8. 显示状态
echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo "访问地址: https://localhost:5446"
echo "健康检查: https://localhost:5446/api/health"
echo "服务状态: https://localhost:5446/api/services"
echo "备份目录: $BACKUP_DIR"
echo "=========================================="
