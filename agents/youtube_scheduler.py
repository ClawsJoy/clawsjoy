#!/usr/bin/env python3
"""定时发布 YouTube 视频"""

import pickle
from pathlib import Path
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CRED_DIR = Path("/mnt/d/clawsjoy/config/youtube")
TOKEN_FILE = CRED_DIR / "token.pickle"
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

# 完整描述
DESCRIPTION = """🇭🇰 2026年香港优才计划迎来重大调整！本期视频详细解读最新政策变化。

📌 本期重点：
✅ 综合计分制最低分数：80分 → 75分
✅ 新增人才清单：金融科技、人工智能、数据科学
✅ 审批时间：6个月 → 3个月

#香港优才计划 #香港身份 #香港移民"""

def upload_video(schedule_hours=0):
    """上传视频，可选定时发布"""
    videos = sorted(VIDEO_DIR.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not videos:
        return {"success": False, "error": "没有找到视频"}
    
    video_path = videos[0]
    
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': '香港优才计划2026｜最新政策解读｜分数降至75分',
            'description': DESCRIPTION,
            'tags': ['香港优才计划', '香港身份', '香港移民'],
            'categoryId': '27'
        },
        'status': {}
    }
    
    if schedule_hours > 0:
        # 定时发布（比如 2 小时后）
        publish_time = (datetime.utcnow() + timedelta(hours=schedule_hours)).isoformat() + 'Z'
        body['status'] = {
            'privacyStatus': 'private',
            'publishAt': publish_time
        }
        print(f"⏰ 定时发布: {publish_time}")
    else:
        # 立即公开
        body['status'] = {'privacyStatus': 'public'}
        print("🚀 立即发布")
    
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    
    return {"success": True, "url": f"https://youtu.be/{response['id']}", "video_id": response['id']}

if __name__ == "__main__":
    import sys
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    result = upload_video(hours)
    print(result)
