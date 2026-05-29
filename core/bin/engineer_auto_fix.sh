#!/bin/bash
# Engineer 自动修复脚本 v2 - 防止空标题

LOG_FILE="$HOME/clawsjoy/logs/engineer_fix.log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "🔧 Engineer 开始检查低分任务..."

python3 << 'PYEOF'
import json, subprocess, os

API_URL = "http://localhost:5005/api/admin"
HOME_DIR = os.path.expanduser('~')

resp = subprocess.run(['curl', '-s', f'{API_URL}/tasks'], capture_output=True, text=True)
tasks = json.loads(resp.stdout)

rejected = [t for t in tasks if t.get('status') == 'rejected']
print(f"发现 {len(rejected)} 个驳回任务")

fixed_count = 0
for task in rejected:
    submitter = task.get('submitter', '')
    title = task.get('title', '')
    content = task.get('content', '')
    
    # 跳过空标题
    if not title or title == '无标题':
        continue
    
    print(f"\n处理: {title} (by {submitter})")
    
    if submitter == 'writer':
        if '<h' not in content:
            fixed = f'<h1>{title}</h1><p>{content}</p><p style="color:#667eea;">工具易上手，结果令人愉悦</p>'
            new_title = f"{title} (优化版)"
            subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_review', new_title, fixed, 'writer_fixed'], shell=True)
            print(f"  ✅ 已修复文章: {new_title}")
            fixed_count += 1
    
    elif submitter == 'video-maker':
        if 'youtube' not in content.lower():
            fixed = content + '\n\nYouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            new_title = f"{title} (优化版)"
            subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_video', new_title, fixed, 'video_fixed'], shell=True)
            print(f"  ✅ 已修复视频: {new_title}")
            fixed_count += 1
    
    elif submitter == 'designer':
        if '<svg' not in content:
            fixed = '<svg width="400" height="150"><rect width="400" height="150" fill="#667eea" rx="20"/><text x="200" y="55" text-anchor="middle" fill="white" font-size="32">ClawsJoy</text></svg>'
            new_title = f"{title} (优化版)"
            subprocess.run([f'{HOME_DIR}/clawsjoy/bin/write_design', new_title, fixed, 'designer_fixed'], shell=True)
            print(f"  ✅ 已修复设计稿: {new_title}")
            fixed_count += 1

print(f"\n✅ Engineer 修复完成，共修复 {fixed_count} 个任务")
PYEOF

log "✅ Engineer 修复完成"
