#!/usr/bin/env python3
"""ClawsJoy Redis 任务队列 - 修复版"""

import json
import redis
import time
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

QUEUE_HIGH = "clawsjoy:tasks:high"
QUEUE_NORMAL = "clawsjoy:tasks:normal"
QUEUE_LOW = "clawsjoy:tasks:low"
QUEUE_DELAY = "clawsjoy:tasks:delay"
QUEUE_PROCESSING = "clawsjoy:tasks:processing"
QUEUE_COMPLETED = "clawsjoy:tasks:completed"
QUEUE_FAILED = "clawsjoy:tasks:failed"


def add_task(task, priority="normal", delay=0):
    task["id"] = f"task_{int(time.time()*1000)}"
    task["created_at"] = datetime.now().isoformat()
    task["retry_count"] = task.get("retry_count", 0)
    task_json = json.dumps(task)

    if delay > 0:
        r.zadd(QUEUE_DELAY, {task_json: time.time() + delay})
    else:
        queue_map = {"high": QUEUE_HIGH, "normal": QUEUE_NORMAL, "low": QUEUE_LOW}
        r.lpush(queue_map.get(priority, QUEUE_NORMAL), task_json)

    print(f"📋 任务添加: {task['id']} ({priority})")
    return task["id"]


def get_task():
    now = time.time()
    delayed = r.zrangebyscore(QUEUE_DELAY, 0, now, start=0, num=1)
    if delayed:
        r.zrem(QUEUE_DELAY, delayed[0])
        return json.loads(delayed[0])

    for q in [QUEUE_HIGH, QUEUE_NORMAL, QUEUE_LOW]:
        task_json = r.rpop(q)
        if task_json:
            task = json.loads(task_json)
            r.hset(QUEUE_PROCESSING, task["id"], task_json)
            return task
    return None


def complete_task(task_id, result):
    task_json = r.hget(QUEUE_PROCESSING, task_id)
    if task_json:
        task = json.loads(task_json)
        task["completed_at"] = datetime.now().isoformat()
        task["result"] = result
        r.hdel(QUEUE_PROCESSING, task_id)
        r.lpush(QUEUE_COMPLETED, json.dumps(task))
        print(f"✅ 任务完成: {task_id}")
        return True
    return False


def fail_task(task_id, error):
    task_json = r.hget(QUEUE_PROCESSING, task_id)
    if task_json:
        task = json.loads(task_json)
        task["error"] = error
        task["failed_at"] = datetime.now().isoformat()
        r.hdel(QUEUE_PROCESSING, task_id)
        r.lpush(QUEUE_FAILED, json.dumps(task))
        print(f"❌ 任务失败: {task_id} - {error}")
        return True
    return False


def execute_task(task):
    """执行具体任务"""
    task_type = task.get("type", "chat")
    prompt = task.get("prompt", "")

    print(f"🔧 执行: {task['id']} ({task_type})")

    try:
        if task_type == "chat":
            # 直接调用 Ollama API
            import requests

            resp = requests.post(
                "http://redis:11434/api/generate",
                json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False},
                timeout=60,
            )
            result = resp.json().get("response", "")
            complete_task(task["id"], result)
            return True

        elif task_type == "code":
            result = subprocess.run(
                f'openclaw infer model run --model ollama/qwen2.5:3b --prompt "{prompt}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            complete_task(task["id"], result.stdout)
            return True

        else:
            complete_task(task["id"], "done")
            return True

    except Exception as e:
        if task.get("retry_count", 0) < 2:
            task["retry_count"] = task.get("retry_count", 0) + 1
            add_task(task, task.get("priority", "normal"), delay=2)
            r.hdel(QUEUE_PROCESSING, task["id"])
        else:
            fail_task(task["id"], str(e))
        return False


def worker_loop():
    print("🚀 Worker 启动，等待任务...")
    while True:
        task = get_task()
        if task:
            execute_task(task)
        time.sleep(1)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/queue/stats":
            stats = {
                "high": r.llen(QUEUE_HIGH),
                "normal": r.llen(QUEUE_NORMAL),
                "low": r.llen(QUEUE_LOW),
                "delay": r.zcard(QUEUE_DELAY),
                "processing": r.hlen(QUEUE_PROCESSING),
                "completed": r.llen(QUEUE_COMPLETED),
                "failed": r.llen(QUEUE_FAILED),
            }
            self.send_json(stats)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/queue/add":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            tid = add_task(
                {"type": data.get("type"), "prompt": data.get("prompt")},
                data.get("priority", "normal"),
            )
            self.send_json({"success": True, "task_id": tid})
        else:
            self.send_error(404)

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        worker_loop()
    else:
        threading.Thread(target=worker_loop, daemon=True).start()
        print("📊 Redis 队列 API: http://redis:8091")
        HTTPServer(("0.0.0.0", 8091), Handler).serve_forever()
