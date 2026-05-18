#!/bin/bash
# 敏感文件备份脚本

BACKUP_DIR="/mnt/d/clawsjoy_sensitive_backup_$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份敏感文件
cp config/youtube/client_secrets.json "$BACKUP_DIR/" 2>/dev/null
cp data/youtube_token.pickle "$BACKUP_DIR/" 2>/dev/null
cp .env "$BACKUP_DIR/" 2>/dev/null

echo "✅ 敏感文件已备份到: $BACKUP_DIR"
