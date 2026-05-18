#!/bin/bash
# 快速恢复

echo "可用的备份文件:"
ls -lh backups/*.tar.gz | tail -5
echo ""
read -p "输入备份文件名: " BACKUP_FILE

if [ -f "backups/$BACKUP_FILE" ]; then
    echo "恢复中..."
    tar -xzf "backups/$BACKUP_FILE" -C /mnt/d/clawsjoy
    echo "✅ 恢复完成，请重启服务"
else
    echo "❌ 文件不存在"
fi
