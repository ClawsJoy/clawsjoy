#!/bin/bash
# ClawsJoy 核心恢复脚本

set -e

echo "=========================================="
echo "ClawsJoy 核心恢复"
echo "=========================================="

# 列出可用备份
BACKUP_DIR="/mnt/d/clawsjoy-backups"
echo ""
echo "可用备份:"
ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "  " $9}' || echo "  无备份文件"

echo ""
read -p "请输入要恢复的备份文件名: " BACKUP_FILE

if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_DIR/$BACKUP_FILE"
    exit 1
fi

echo ""
echo "目标目录: /mnt/d/clawsjoy_clean"
read -p "确认恢复？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消恢复"
    exit 0
fi

echo ""
echo "1. 解压备份..."
TEMP_DIR="/tmp/restore_temp"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
tar -xzf "$BACKUP_DIR/$BACKUP_FILE" -C "$TEMP_DIR"

echo "2. 恢复核心代码..."
cp -r "$TEMP_DIR"/*/lib "$TEMP_DIR"/*/intelligence "$TEMP_DIR"/*/agents "$TEMP_DIR"/*/agent_core . 2>/dev/null

echo "3. 恢复技能..."
cp -r "$TEMP_DIR"/*/skills/* skills/

echo "4. 恢复配置..."
cp -r "$TEMP_DIR"/*/config/driver config/
cp -r "$TEMP_DIR"/*/config/intelligence config/ 2>/dev/null

echo "5. 恢复 Web 界面..."
cp "$TEMP_DIR"/*/web_dashboard.py .
cp -r "$TEMP_DIR"/*/web .
cp "$TEMP_DIR"/*/app_v4.py .
cp "$TEMP_DIR"/*/bin/active_runner.py bin/ 2>/dev/null

echo "6. 恢复文档..."
cp -r "$TEMP_DIR"/*/docs .
cp "$TEMP_DIR"/*/*.md .
cp "$TEMP_DIR"/*/VERSION .
cp "$TEMP_DIR"/*/requirements.txt . 2>/dev/null

echo "7. 清理..."
rm -rf "$TEMP_DIR"

echo ""
echo "✅ 恢复完成"
echo "请手动恢复 data/ 和 memory/ 数据（如有需要）"
echo "=========================================="

