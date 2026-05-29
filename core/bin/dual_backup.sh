#!/bin/bash
# 双地备份：D盘本地 + C盘 Windows 分区

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="clawsjoy_backup_$DATE.tar.gz"

# 备份到 D 盘
cd /mnt/d/clawsjoy
tar -czf "backups/${BACKUP_NAME}" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="logs/*.log" \
    data/ marketplace/ agent_gateway_web.py 2>/dev/null

# 同步到 C 盘（Windows 用户目录）
cp "backups/${BACKUP_NAME}" /mnt/c/Users/flybo/Desktop/

echo "[$DATE] 双备份完成: D盘 + C盘桌面" >> logs/backup.log
