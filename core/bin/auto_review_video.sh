#!/bin/bash
# Reviewer 自动预审视频

echo "🤖 Reviewer 自动预审视频..."

curl -s http://localhost:5005/api/admin/tasks | python3 << PYEOF
import sys,json

tasks = json.load(sys.stdin)
videos = [t for t in tasks if t.get('submitter') in ['video-maker', 'youtube'] and t.get('status') == 'pending']

print(f"发现 {len(videos)} 个待审核视频")

for v in videos:
    title = v.get('title', '')
    youtube_id = v.get('youtube_id', '')
    
    # 自动评分规则
    score = 60  # 基础分
    if youtube_id:
        score += 20  # 有有效链接 +20
    if len(title) > 5:
        score += 5   # 标题合理 +5
    
    print(f"\n📹 {title}")
    print(f"   建议评分: {score}/100")
    print(f"   YouTube ID: {youtube_id or '无'}")
    
    if score >= 80:
        print(f"   建议: ✅ 自动通过")
    elif score >= 60:
        print(f"   建议: ⏳ 需人工审核")
    else:
        print(f"   建议: ❌ 驳回")

PYEOF

echo ""
echo "📋 请登录审核看板手动确认"
