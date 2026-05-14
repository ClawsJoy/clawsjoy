#!/bin/bash
# 六大核心库自动备份

BACKUP_DIR="/mnt/d/clawsjoy/backups/core_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份核心数据
cp data/agent_brain.json "$BACKUP_DIR/" 2>/dev/null
cp data/keywords.json "$BACKUP_DIR/" 2>/dev/null
cp data/lightweight_kb.json "$BACKUP_DIR/" 2>/dev/null
cp data/verified_skills.json "$BACKUP_DIR/" 2>/dev/null
cp data/simple_vector.json "$BACKUP_DIR/" 2>/dev/null

# 压缩
tar -czf "$BACKUP_DIR.tar.gz" -C backups "$(basename "$BACKUP_DIR")" 2>/dev/null
rm -rf "$BACKUP_DIR"

# 只保留最近10个备份
ls -t backups/core_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

echo "[$(date)] 备份完成: $BACKUP_DIR.tar.gz" >> logs/backup.log
