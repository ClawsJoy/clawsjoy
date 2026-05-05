#!/usr/bin/env python3
import json
import requests
from datetime import datetime

API_URL = "http://redis:5005/api/admin/tasks"


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
    merged_content = "<h1>今日宣传片合集</h1>\n"
    for idx, t in enumerate(tasks, 1):
        merged_content += f"<h2>{idx}. {t.get('title', '宣传片')}</h2>\n"
        merged_content += t.get("content", "") + "\n\n"
        merged_content += "<hr/>\n"
    return main_title, merged_content


def main():
    tasks = get_approved_tasks()
    if not tasks:
        print("今天没有已通过的宣传片任务")
        return

    title, content = merge_articles(tasks)
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{title}</title></head>
<body>
{content}
</body>
</html>"""

    with open("/tmp/wechat_publish.html", "w") as f:
        f.write(html)

    print("✅ 文章已生成: /tmp/wechat_publish.html")
    print("📢 浏览器打开该文件，全选复制，粘贴到公众号草稿箱后发布")


if __name__ == "__main__":
    main()
