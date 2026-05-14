#!/bin/bash
cd /mnt/d/clawsjoy

# 只备份核心数据文件，不提交代码
cp data/agent_brain.json data/agent_brain.json.bak
cp data/keywords.json data/keywords.json.bak

git add data/*.json 2>/dev/null
git commit -m "chore: auto backup core data $(date +%Y%m%d_%H%M%S)" 2>/dev/null
git push origin main 2>/dev/null

echo "[$(date)] Git 备份完成" >> logs/git_backup.log
