#!/bin/bash
# 自动发布审核通过的内容到网站

API_URL="http://localhost:5005/api/admin"
WEBSITE_DIR="$HOME/.openclaw/web"
PUBLISHED_DIR="$WEBSITE_DIR/published"
LOG_FILE="$HOME/clawsjoy/logs/auto_publish.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "=== 检查新通过的内容并发布到网站 ==="

# 获取最近通过的待发布内容
python3 << PYEOF
import json, os, subprocess
from datetime import datetime

PUBLISHED_DIR = os.path.expanduser('~/.openclaw/web/published')
os.makedirs(PUBLISHED_DIR, exist_ok=True)

# 获取所有任务
resp = subprocess.run(['curl', '-s', 'http://localhost:5005/api/admin/tasks'], capture_output=True, text=True)
tasks = json.loads(resp.stdout)

# 创建内容索引
content_index = {
    'designs': [],
    'articles': [],
    'videos': [],
    'updated_at': datetime.now().isoformat()
}

for t in tasks:
    if t.get('status') == 'approved':
        item = {
            'id': t.get('id'),
            'title': t.get('title'),
            'content': t.get('content'),
            'submitter': t.get('submitter'),
            'date': t.get('created_at', ''),
            'score': t.get('score', '未评分')
        }
        if t.get('submitter') == 'designer':
            content_index['designs'].append(item)
        elif t.get('submitter') == 'writer':
            content_index['articles'].append(item)
        elif t.get('submitter') == 'video-maker':
            content_index['videos'].append(item)

# 保存索引
with open(os.path.join(PUBLISHED_DIR, 'content_index.json'), 'w') as f:
    json.dump(content_index, f, indent=2, ensure_ascii=False)

print(f"✅ 内容索引已更新")
print(f"   设计案例: {len(content_index['designs'])} 个")
print(f"   品牌文章: {len(content_index['articles'])} 个")
print(f"   宣传视频: {len(content_index['videos'])} 个")
PYEOF

log "✅ 网站内容发布完成"
