#!/bin/bash
echo "清理前: $(du -sh /home/flybo/clawsjoy_v5)"

# 1. 清理 ComfyUI 缓存
find tools/ComfyUI -name "*.pyc" -delete
find tools/ComfyUI -name "__pycache__" -type d -exec rm -rf {} +

# 2. 清理旧的日志
find logs/ -name "*.log" -mtime +30 -delete

# 3. 清理输出目录
rm -rf output/* outputs/* dreamshaper_outputs/*

# 4. 清理重复的数据库 (先备份)
mkdir -p /backup/dbs
cp data/*.db /backup/dbs/ 2>/dev/null

echo "清理后: $(du -sh /home/flybo/clawsjoy_v5)"
