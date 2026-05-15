#!/usr/bin/env python3
import json
import requests
import os
from datetime import datetime

API_URL = "http://redis:5005/api/admin/tasks"
APP_ID = os.environ.get("WECHAT_APP_ID")
APP_SECRET = os.environ.get("WECHAT_APP_SECRET")
IMAGE_PATH = "/home/flybo/.openclaw/web/images/香港/香港_1.jpg"  # 换成你本地的小图


def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    return requests.get(url).json().get("access_token")


def upload_thumb(access_token):
    with open(IMAGE_PATH, "rb") as f:
        resp = requests.post(
            f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=thumb",
            files={"media": f},
        )
    return resp.json().get("thumb_media_id")


def create_draft(access_token, title, content, thumb_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    body = {
        "articles": [
            {
                "title": title,
                "author": "ClawsJoy",
                "digest": content[:120],
                "content": content,
                "thumb_media_id": thumb_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 1,
            }
        ]
    }
    return requests.post(url, json=body).json()


def get_approved_tasks():
    try:
        resp = requests.get(API_URL, timeout=5)
        tasks = resp.json()
        today = datetime.now().strftime("%Y-%m-%d")
        approved = []
        for t in tasks:
            if t.get("status") == "approved" and "宣传片" in t.get("title", ""):
                created = t.get("created_at", "")[:10]
                if created == today:
                    approved.append(t)
        return approved
    except Exception as e:
        print(f"错误: {e}")
        return []


def merge_articles(tasks):
    if not tasks:
        return None, None
    main_title = tasks[0].get("title", "ClawsJoy 今日宣传片合集")
    merged = "<h1>今日宣传片合集</h1>\n"
    for idx, t in enumerate(tasks, 1):
        merged += f"<h2>{idx}. {t.get('title', '宣传片')}</h2>\n"
        merged += t.get("content", "") + "\n\n"
        merged += "<hr/>\n"
    return main_title, merged


def main():
    if not APP_ID or not APP_SECRET:
        print("❌ 请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        return

    tasks = get_approved_tasks()
    if not tasks:
        print("今天没有已通过的宣传片任务")
        return

    title, content = merge_articles(tasks)
    print(f"生成文章: {title}")

    token = get_access_token()
    if not token:
        print("❌ 获取 access_token 失败")
        return

    thumb_id = upload_thumb(token)
    if not thumb_id:
        print("❌ 上传封面失败")
        return

    result = create_draft(token, title, content, thumb_id)
    print("草稿箱结果:", result)

    if result.get("errcode") == 0:
        print("✅ 草稿已保存，请登录公众号后台发布")
    else:
        print("❌ 创建草稿失败")


if __name__ == "__main__":
    main()
