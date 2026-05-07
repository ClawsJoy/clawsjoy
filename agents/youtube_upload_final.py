#!/usr/bin/env python3
"""YouTube 视频上传 - 完整版描述"""

import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CRED_DIR = Path("/mnt/d/clawsjoy/config/youtube")
TOKEN_FILE = CRED_DIR / "token.pickle"
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

DESCRIPTION = """🇭🇰 2026年香港优才计划迎来重大调整！本期视频详细解读最新政策变化。

📌 **本期重点：**
✅ 综合计分制最低分数：80分 → 75分（门槛降低）
✅ 新增人才清单：金融科技、人工智能、数据科学（直接加30分）
✅ 审批时间：6个月 → 3个月（速度翻倍）
✅ 2025年获批数据：3421人获批，成功率约38%

🎯 **谁适合申请？**
• 本科及以上学历
• 2年以上工作经验
• 综合评分75分以上
• 有专业背景或特殊才能

📋 **申请流程（4步）：**
1️⃣ 自我评估分数
2️⃣ 准备学历、工作证明
3️⃣ 撰写来港计划书
4️⃣ 在线提交申请

💡 **加分提示：**
• 世界百强名校毕业 → +30分
• 知名企业工作经验 → +20分
• 符合人才清单专业 → +30分

🔔 订阅频道，获取最新香港政策资讯！

📩 评论区留言你的分数，免费帮你评估成功率！

#香港优才计划 #香港身份 #香港移民 #优才计划2026 #香港人才清单 #香港签证 #香港生活 #香港工作 #高才通 #专才计划 #香港留学"""

def upload_video():
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    videos = sorted(VIDEO_DIR.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not videos:
        print("❌ 没有找到视频")
        return
    
    video_path = videos[0]
    print(f"📤 上传视频: {video_path.name}")
    
    body = {
        'snippet': {
            'title': '香港优才计划2026｜最新政策解读｜分数降至75分｜3个月获批',
            'description': DESCRIPTION,
            'tags': ['香港优才计划', '香港身份', '香港移民', '优才计划2026', '香港人才清单', '香港签证', '香港生活'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'public'  # 改为公开
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
        print(f"✅ 上传成功！")
        print(f"   视频ID: {response['id']}")
        print(f"   链接: https://youtu.be/{response['id']}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")

if __name__ == "__main__":
    upload_video()
