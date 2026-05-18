#!/bin/bash
# 自动备份到多个位置

BACKUP_DIR="/mnt/d/clawsjoy/backups/auto"
mkdir -p "$BACKUP_DIR"

# 备份数据
tar -czf "$BACKUP_DIR/data_$(date +%Y%m%d_%H%M%S).tar.gz" \
    /mnt/d/clawsjoy/data/ \
    /mnt/d/clawsjoy/marketplace/ \
    2>/dev/null

# 保留最近7天，删除更旧的
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "[$(date)] 自动备份完成" >> /mnt/d/clawsjoy/logs/backup.log
