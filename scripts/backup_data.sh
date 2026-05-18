#!/bin/bash
# ClawsJoy 数据备份脚本

BACKUP_DIR="/mnt/d/clawsjoy-backups/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "ClawsJoy 数据备份"
echo "=========================================="

# 备份数据
echo "1. 备份 data/ 目录..."
tar -czf "$BACKUP_DIR/data_$TIMESTAMP.tar.gz" data/ 2>/dev/null
echo "   ✅ data/ 已备份"

# 备份记忆
echo "2. 备份 memory/ 目录..."
tar -czf "$BACKUP_DIR/memory_$TIMESTAMP.tar.gz" memory/ 2>/dev/null
echo "   ✅ memory/ 已备份"

# 备份配置
echo "3. 备份 config/ 目录..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" config/ 2>/dev/null
echo "   ✅ config/ 已备份"

# 备份向量库
echo "4. 备份向量库..."
tar -czf "$BACKUP_DIR/vector_$TIMESTAMP.tar.gz" data/vector_kb/ 2>/dev/null
echo "   ✅ 向量库已备份"

# 清理旧备份（保留最近7天）
echo ""
echo "5. 清理旧备份（保留7天）..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo ""
echo "✅ 备份完成: $BACKUP_DIR/data_$TIMESTAMP.tar.gz"
echo "=========================================="
