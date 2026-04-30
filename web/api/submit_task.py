#!/usr/bin/env python3
import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

TASK_QUEUE_DIR = "/tmp/tenants/queue"
REVIEW_QUEUE_FILE = os.path.expanduser("~/.openclaw/web/review/data/queue.json")
os.makedirs(TASK_QUEUE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REVIEW_QUEUE_FILE), exist_ok=True)

def add_to_review_queue(tenant, city, style):
    if os.path.exists(REVIEW_QUEUE_FILE):
        with open(REVIEW_QUEUE_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {"pending_review": [], "pending_final": [], "completed": []}
    
    task = {
        "id": int(time.time() * 1000),
        "title": f"{city}宣传片",
        "content": f"城市: {city}, 风格: {style}",
        "submitter": f"租户_{tenant}",
        "tenant": tenant,
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    data["pending_review"].append(task)
    with open(REVIEW_QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ 审核队列已写入: {task['title']}")

class TaskHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/submit_task":
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            tenant = data.get('tenant', '租户1')
            task_type = data.get('task_type', 'full_promo')
            city = data.get('city', 'hongkong')
            style = data.get('style', 'tech')

            # 1. 写入执行队列
            timestamp = int(time.time())
            task_file = f"{TASK_QUEUE_DIR}/task_{tenant}_{timestamp}.json"
            with open(task_file, 'w') as f:
                json.dump({"tenant": tenant, "task_type": task_type, "city": city, "style": style}, f)

            # 2. 写入审核队列
            add_to_review_queue(tenant, city, style)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("🚀 任务API启动（同时写入审核队列）: http://localhost:8084/api/submit_task")
    HTTPServer(("0.0.0.0", 8084), TaskHandler).serve_forever()
