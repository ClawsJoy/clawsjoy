#!/bin/bash
# 清理被驳回的垃圾作品（30天以上的）

LOG_FILE="$HOME/clawsjoy/logs/cleanup_rejected.log"
log() { echo "[$(date)] $1" | tee -a "$LOG_FILE"; }

log "🗑️ 开始清理被驳回的垃圾作品..."

python3 << 'PYEOF'
import json, os, shutil
from datetime import datetime, timedelta

queue_file = os.path.expanduser('~/.openclaw/web/review/data/queue.json')
TRASH_DIR = os.path.expanduser('~/.openclaw/trash')
os.makedirs(TRASH_DIR, exist_ok=True)

with open(queue_file, 'r') as f:
    data = json.load(f)

cutoff = datetime.now() - timedelta(days=30)
cleaned_count = 0
archived_count = 0

new_completed = []
for task in data.get('completed', []):
    status = task.get('status', '')
    created_at = task.get('created_at', '')
    
    try:
        created_date = datetime.strptime(created_at[:10], '%Y-%m-%d')
    except:
        created_date = datetime.now()
    
    # 被驳回且超过30天
    if status == 'rejected' and created_date < cutoff:
        # 归档到垃圾箱（不直接删除）
        archive_file = os.path.join(TRASH_DIR, f"rejected_{task.get('id')}_{created_at[:10]}.json")
        with open(archive_file, 'w') as f:
            json.dump(task, f, indent=2)
        archived_count += 1
        cleaned_count += 1
        continue  # 跳过，不保留
    
    new_completed.append(task)

data['completed'] = new_completed

with open(queue_file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"📦 归档到垃圾箱: {archived_count} 个")
print(f"🗑️ 已清理: {cleaned_count} 个")
print(f"📁 垃圾箱位置: {TRASH_DIR}")
PYEOF

log "✅ 清理完成"
