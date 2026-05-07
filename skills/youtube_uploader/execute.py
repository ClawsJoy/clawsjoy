#!/usr/bin/env python3
"""YouTube 上传 Skill - 自动发布视频"""

import pickle
import sys
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CRED_DIR = Path("/mnt/d/clawsjoy/config/youtube")
TOKEN_FILE = CRED_DIR / "token.pickle"
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

DESCRIPTION_TEMPLATE = """🇭🇰 2026年香港{topic}迎来重大调整！本期视频详细解读最新政策变化。

📌 本期重点：
✅ {key_points}

🎯 谁适合申请？
• 本科及以上学历
• 2年以上工作经验
• 综合评分75分以上

💡 申请流程：
1️⃣ 自我评估分数
2️⃣ 准备学历、工作证明
3️⃣ 撰写来港计划书
4️⃣ 在线提交申请

🔔 订阅频道，获取最新香港政策资讯！

#香港优才计划 #香港身份 #香港移民 #{topic_tag} #香港人才清单"""

TAGS = ['香港优才计划', '香港身份', '香港移民', '香港人才计划', '香港签证']


def get_latest_video():
    videos = sorted(VIDEO_DIR.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    return videos[0] if videos else None


def upload_video(topic="香港优才计划", key_points="", privacy="unlisted"):
    """上传视频到 YouTube"""
    
    # 获取最新视频
    video_path = get_latest_video()
    if not video_path:
        return {"success": False, "error": "No video found"}
    
    # 加载认证凭据
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    # 生成描述
    description = DESCRIPTION_TEMPLATE.format(
        topic=topic,
        key_points=key_points or "综合计分制最低分数：80分 → 75分",
        topic_tag=topic.replace("计划", "")
    )
    
    # 视频元数据
    body = {
        'snippet': {
            'title': f'{topic}2026｜最新政策解读｜分数降至75分｜3个月获批',
            'description': description,
            'tags': TAGS,
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': privacy  # public, unlisted, private
        }
    }
    
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    
    try:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        response = request.execute()
        return {
            "success": True,
            "video_id": response['id'],
            "url": f"https://youtu.be/{response['id']}",
            "title": body['snippet']['title']
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute(params):
    """Skill 入口函数"""
    topic = params.get('topic', '香港优才计划')
    key_points = params.get('key_points', '')
    privacy = params.get('privacy', 'unlisted')
    
    result = upload_video(topic, key_points, privacy)
    return result


if __name__ == "__main__":
    # 命令行测试
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {"topic": "香港优才计划", "privacy": "unlisted"}
    
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False))
