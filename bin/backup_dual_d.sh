#!/bin/bash
# D 盘双位置备份：项目内 + 项目外独立目录

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="clawsjoy_backup_$DATE.tar.gz"

# 备份到项目内
cd /mnt/d/clawsjoy
mkdir -p backups
tar -czf "backups/${BACKUP_NAME}" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="logs/*.log" \
    data/ marketplace/ agent_gateway_web.py 2>/dev/null

# 备份到外部独立目录
tar -czf "/mnt/d/clawsjoy_backups/${BACKUP_NAME}" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="logs/*.log" \
    data/ marketplace/ agent_gateway_web.py 2>/dev/null

# 保留各目录最近 10 个
cd /mnt/d/clawsjoy/backups
ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

cd /mnt/d/clawsjoy_backups
ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

echo "[$DATE] D盘双位置备份完成" >> /mnt/d/clawsjoy/logs/backup.log
