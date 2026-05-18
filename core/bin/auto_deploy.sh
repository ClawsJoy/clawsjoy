#!/bin/bash
# 监听审核通过的任务，自动执行部署

API_URL="http://localhost:5005/api/admin"
LOG_FILE="$HOME/clawsjoy/logs/auto_deploy.log"

log() { echo "[$(date)] $1" | tee -a "$LOG_FILE"; }

# 获取最新通过的 engineer 任务
curl -s "$API_URL/tasks" | python3 << PYEOF
import json, subprocess, os

API_URL = "http://localhost:5005/api/admin"
resp = subprocess.run(['curl', '-s', f'{API_URL}/tasks'], capture_output=True, text=True)
tasks = json.loads(resp.stdout)

for task in tasks:
    if task.get('submitter') == 'engineer' and task.get('status') == 'approved':
        # 检查是否已执行过
        if task.get('deployed'):
            continue
        
        title = task.get('title', '')
        command = task.get('command', '')
        preview_url = task.get('preview_url', '')
        
        print(f"🚀 执行部署: {title}")
        print(f"📋 命令: {command}")
        
        # 执行命令
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # 标记已部署
        task['deployed'] = True
        task['deploy_result'] = result.returncode == 0
        task['deploy_output'] = result.stdout[:500]
        
        print(f"✅ 部署完成: {'成功' if result.returncode == 0 else '失败'}")
PYEOF

log "自动部署检查完成"
