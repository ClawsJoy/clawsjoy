#!/bin/bash
# 恢复最近的核心库备份

cd /mnt/d/clawsjoy

# 找到最新备份
LATEST=$(ls -t backups/core_*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    echo "❌ 没有找到备份文件"
    exit 1
fi

echo "📦 恢复备份: $LATEST"
tar -xzf "$LATEST" -C /tmp/

# 恢复文件
BACKUP_DIR=$(basename "$LATEST" .tar.gz)
cp /tmp/$BACKUP_DIR/*.json data/

echo "✅ 恢复完成"
