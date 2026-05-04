#!/usr/bin/env python3
import json
import requests
import os
from datetime import datetime

API_URL = "http://redis:5005/api/admin/tasks"
APP_ID = os.environ.get("WECHAT_APP_ID")
APP_SECRET = os.environ.get("WECHAT_APP_SECRET")

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    resp = requests.get(url)
    data = resp.json()
    return data.get("access_token")

def upload_thumb(access_token, thumb_path):
    # 简单模拟：实际需要先上传临时素材获得 media_id
    return "test_media_id"

def publish_article(title, content, access_token):
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token={access_token}"
    body = {
        "filter": {"is_to_all": True},
        "text": {"content": f"{title}\n\n{content}"},
        "msgtype": "text"
    }
    # 这里用文本方式发送，正式可用图文消息
    resp = requests.post(url, json=body)
    return resp.json()

def get_approved_tasks():
    try:
        resp = requests.get(API_URL, timeout=5)
        tasks = resp.json()
        today = datetime.now().strftime("%Y-%m-%d")
        approved = []
        for t in tasks:
            if t.get('status') == 'approved' and '宣传片' in t.get('title', ''):
                created = t.get('created_at', '')[:10]
                if created == today:
                    approved.append(t)
        return approved
    except Exception as e:
        print(f"错误: {e}")
        return []

def merge_articles(tasks):
    if not tasks:
        return None, None
    main_title = tasks[0].get('title', 'ClawsJoy 今日宣传片合集')
    merged_content = "<h1>今日宣传片合集</h1>\n"
    for idx, t in enumerate(tasks, 1):
        merged_content += f"<h2>{idx}. {t.get('title', '宣传片')}</h2>\n"
        merged_content += t.get('content', '') + "\n\n"
        merged_content += "<hr/>\n"
    return main_title, merged_content

def mark_published(task_ids):
    print(f"✅ 已将 {task_ids} 标记为已发布")

def main():
    tasks = get_approved_tasks()
    if not tasks:
        print("今天没有已通过的宣传片任务")
        return

    if not APP_ID or not APP_SECRET:
        print("❌ 未设置 WECHAT_APP_ID 或 WECHAT_APP_SECRET")
        return

    title, content = merge_articles(tasks)
    print(f"生成合并文章: {title} (长度 {len(content)})")

    access_token = get_access_token()
    if not access_token:
        print("❌ 获取 access_token 失败")
        return

    # 正式发布
    result = publish_article(title, content, access_token)
    print("发布结果:", result)

    if result.get("errcode") == 0:
        mark_published([t['id'] for t in tasks])
    else:
        print("❌ 发布失败")

if __name__ == "__main__":
    main()
