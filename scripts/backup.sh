#!/bin/bash
# ClawsJoy 数据备份脚本

BACKUP_DIR="/home/flybo/clawsjoy_v5/backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/clawsjoy_backup_$DATE.tar.gz"

# 备份核心数据
tar -czf "$BACKUP_FILE" \
    --exclude="*.log" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="data/vector_kb" \
    --exclude="logs" \
    config/ core/ agents/ skills/ 2>/dev/null

# 保留最近7天的备份
find "$BACKUP_DIR" -name "clawsjoy_backup_*.tar.gz" -mtime +7 -delete

echo "[$DATE] 备份完成: $BACKUP_FILE" >> logs/backup.log
