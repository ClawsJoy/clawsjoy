#!/usr/bin/env python3
"""自然语言 Agent - 修复导入"""

import json
import requests
import subprocess
import sys
import re
import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CRED_DIR = Path("/mnt/d/clawsjoy/config/youtube")
TOKEN_FILE = CRED_DIR / "token.pickle"
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

def upload_to_youtube(topic="香港优才计划", privacy="unlisted"):
    """直接上传视频"""
    videos = sorted(VIDEO_DIR.glob("hk_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not videos:
        return {"success": False, "error": "没有找到视频"}
    
    video_path = videos[0]
    
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    description = f"""🇭🇰 2026年香港{topic}迎来重大调整！本期视频详细解读最新政策变化。

✅ 综合计分制最低分数：80分 → 75分
✅ 新增人才清单：金融科技、人工智能、数据科学
✅ 审批时间：6个月 → 3个月

#香港优才计划 #香港身份 #香港移民"""

    body = {
        'snippet': {
            'title': f'{topic}2026｜最新政策解读',
            'description': description,
            'tags': ['香港优才计划', '香港身份', '香港移民'],
            'categoryId': '27'
        },
        'status': {'privacyStatus': privacy}
    }
    
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    
    return {"success": True, "url": f"https://youtu.be/{response['id']}", "video_id": response['id']}

def understand_intent(text):
    text_lower = text.lower()
    if re.search(r'上传|发布|upload|youtube', text_lower):
        return {"intent": "upload", "topic": extract_topic(text)}
    elif re.search(r'生成|制作|make|视频', text_lower):
        return {"intent": "make", "topic": extract_topic(text)}
    elif re.search(r'采集|收集|crawl', text_lower):
        return {"intent": "collect", "topic": None}
    else:
        return {"intent": "unknown", "topic": None}

def extract_topic(text):
    if "优才" in text:
        return "香港优才计划"
    elif "高才" in text:
        return "香港高才通计划"
    elif "留学" in text:
        return "香港留学"
    return "香港优才计划"

def execute(intent, topic):
    if intent == "upload":
        result = upload_to_youtube(topic)
        if result.get("success"):
            return f"✅ 视频已发布！\n   链接: {result['url']}"
        return f"❌ 失败: {result.get('error')}"
    elif intent == "make":
        resp = requests.post("http://localhost:8105/api/promo/make", 
            json={"topic": topic}, timeout=300)
        data = resp.json()
        if data.get("success"):
            return f"🎬 视频已生成！\n   地址: http://localhost:8082{data['video_url']}"
        return f"❌ 失败: {data.get('error')}"
    elif intent == "collect":
        subprocess.run(["python3", "spiders/hk_spider.py"])
        return "📰 采集完成"
    return "❌ 无法理解"

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "上传视频"
    print(f"📝: {text}")
    result = understand_intent(text)
    print(f"🎯: {result}")
    print(execute(result.get("intent"), result.get("topic")))

def clean_script(script):
    """清理脚本中的乱码"""
    import re
    script = re.sub(r'#{3,}', '', script)
    script = re.sub(r'\*{3,}', '', script)
    script = re.sub(r'AA|BB|CC', '', script)
    script = re.sub(r'\[.*?\]', '', script)
    script = re.sub(r'\n{3,}', '\n\n', script)
    return script.strip()
