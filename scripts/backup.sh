#!/bin/bash
BACKUP_DIR="/home/flybo/clawsjoy_v5/backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/clawsjoy_backup_$DATE.tar.gz"

# 备份所有数据（包括向量库）
tar -czf "$BACKUP_FILE" \
    --exclude="*.log" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="logs" \
    --exclude="backups" \
    config/ core/ agents/ skills/ data/ 2>/dev/null

# 保留最近7天
find "$BACKUP_DIR" -name "clawsjoy_backup_*.tar.gz" -mtime +7 -delete

echo "[$DATE] 备份完成: $BACKUP_FILE" >> logs/backup.log
# 验证备份大小
ls -lh "$BACKUP_FILE" >> logs/backup.log
