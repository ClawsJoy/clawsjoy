#!/bin/bash
# ClawsJoy 数据备份脚本

BACKUP_DIR="/mnt/d/backups/clawsjoy/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 备份开始: $BACKUP_DIR"

# 备份关键词库
cp data/keywords.json "$BACKUP_DIR/" 2>/dev/null
cp data/keyword_pending.json "$BACKUP_DIR/" 2>/dev/null

# 备份 URL 库
cp data/urls/discovered.json "$BACKUP_DIR/" 2>/dev/null
cp data/collected_urls.json "$BACKUP_DIR/" 2>/dev/null

# 备份租户配置
cp -r tenants "$BACKUP_DIR/" 2>/dev/null

# 备份配置文件
cp config/*.json "$BACKUP_DIR/" 2>/dev/null

# 备份技能关键词
cp data/skill_keywords.json "$BACKUP_DIR/" 2>/dev/null

# 记录备份信息
echo "备份时间: $(date)" > "$BACKUP_DIR/backup.info"
echo "关键词数量: $(jq '.categories | map(.keywords | length) | add' data/keywords.json 2>/dev/null || echo 0)" >> "$BACKUP_DIR/backup.info"
echo "URL 数量: $(jq length data/urls/discovered.json 2>/dev/null || echo 0)" >> "$BACKUP_DIR/backup.info"

# 压缩
cd /mnt/d/backups/clawsjoy
tar -czf "$(date +%Y%m%d_%H%M%S).tar.gz" "$(basename "$BACKUP_DIR")" 2>/dev/null
rm -rf "$BACKUP_DIR"

echo "✅ 备份完成: /mnt/d/backups/clawsjoy/$(date +%Y%m%d_%H%M%S).tar.gz"
echo "📊 保留最近 30 天的备份"
find /mnt/d/backups/clawsjoy -name "*.tar.gz" -mtime +30 -delete
