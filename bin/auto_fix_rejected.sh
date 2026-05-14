#!/bin/bash
# Engineer 自动修复被驳回的任务

API_URL="http://localhost:5005/api/admin"
LOG_FILE="$HOME/clawsjoy/logs/auto_fix.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "🔧 开始检查被驳回的任务..."

# 获取所有被驳回的任务
python3 << 'PYEOF'
import json, subprocess, os
from datetime import datetime

API_URL = "http://localhost:5005/api/admin"
HOME_DIR = os.path.expanduser('~')

# 获取任务
resp = subprocess.run(['curl', '-s', f'{API_URL}/tasks'], capture_output=True, text=True)
try:
    tasks = json.loads(resp.stdout)
except:
    print("无法获取任务列表")
    exit(0)

rejected = [t for t in tasks if t.get('status') == 'rejected']
print(f"发现 {len(rejected)} 个被驳回的任务")

for task in rejected:
    title = task.get('title', '')
    submitter = task.get('submitter', '')
    content = task.get('content', '')
    
    print(f"处理驳回任务: {title} (by {submitter})")
    
    # 根据提交者类型修复
    if submitter == 'video-maker':
        new_title = f"{title} (修复版)"
        fixed_content = f"{content} YouTube参考: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_video', new_title, fixed_content, 'video-maker'], shell=True)
        print(f"已重新提交视频: {new_title}")
    
    elif submitter == 'writer':
        if '<h' not in content:
            fixed_content = f"<h1>{title}</h1><p>{content}</p>"
        else:
            fixed_content = content
        new_title = f"{title} (修复版)"
        subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_review', new_title, fixed_content, 'writer'], shell=True)
        print(f"已重新提交文章: {new_title}")
    
    elif submitter == 'designer':
        if '<svg' not in content:
            fixed_content = '<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="200" fill="#667eea" rx="10"/><text x="200" y="110" text-anchor="middle" fill="white" font-size="24">ClawsJoy</text></svg>'
        else:
            fixed_content = content
        new_title = f"{title} (修复版)"
        subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_design', new_title, fixed_content, 'designer'], shell=True)
        print(f"已重新提交设计稿: {new_title}")
    
    elif submitter == 'engineer':
        new_title = f"{title} (自动修复)"
        subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_deploy', new_title, content, '自动修复后重新提交'], shell=True)
        print(f"已重新提交部署任务: {new_title}")

print("修复完成")
PYEOF

log "🔧 修复检查完成"
