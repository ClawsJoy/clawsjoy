#!/usr/bin/env python3
"""
ClawsJoy Redis 任务队列系统
支持优先级、重试、延迟任务
"""

import json
import redis
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

# Redis 连接
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping()
    print("✅ Redis 连接成功")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
    sys.exit(1)

# 队列名称
QUEUE_HIGH = "clawsjoy:tasks:high"
QUEUE_NORMAL = "clawsjoy:tasks:normal"
QUEUE_LOW = "clawsjoy:tasks:low"
QUEUE_DELAY = "clawsjoy:tasks:delay"
QUEUE_PROCESSING = "clawsjoy:tasks:processing"
QUEUE_FAILED = "clawsjoy:tasks:failed"
QUEUE_COMPLETED = "clawsjoy:tasks:completed"

# 统计键
STATS_TOTAL = "clawsjoy:stats:total"
STATS_SUCCESS = "clawsjoy:stats:success"
STATS_FAILED = "clawsjoy:stats:failed"

class RedisTaskQueue:
    """Redis 任务队列"""
    
    def __init__(self):
        self.r = r
    
    def add_task(self, task: dict, priority: str = "normal", delay: int = 0):
        """添加任务
        priority: high, normal, low
        delay: 延迟秒数
        """
        task["id"] = task.get("id", f"task_{int(time.time()*1000)}")
        task["created_at"] = datetime.now().isoformat()
        task["priority"] = priority
        task["retry_count"] = task.get("retry_count", 0)
        task["max_retries"] = task.get("max_retries", 3)
        
        task_json = json.dumps(task, ensure_ascii=False)
        
        if delay > 0:
            # 延迟任务
            self.r.zadd(QUEUE_DELAY, {task_json: time.time() + delay})
        else:
            # 立即任务
            queue_map = {
                "high": QUEUE_HIGH,
                "normal": QUEUE_NORMAL,
                "low": QUEUE_LOW
            }
            self.r.lpush(queue_map.get(priority, QUEUE_NORMAL), task_json)
        
        # 统计
        self.r.incr(STATS_TOTAL)
        print(f"📋 任务已添加: {task['id']} (优先级: {priority})")
        return task["id"]
    
    def get_task(self, timeout: int = 5):
        """获取任务（优先级: high > normal > low）"""
        # 1. 检查延迟任务
        now = time.time()
        delayed = self.r.zrangebyscore(QUEUE_DELAY, 0, now, start=0, num=1)
        if delayed:
            task_json = delayed[0]
            self.r.zrem(QUEUE_DELAY, task_json)
            return json.loads(task_json)
        
        # 2. 按优先级获取
        for queue in [QUEUE_HIGH, QUEUE_NORMAL, QUEUE_LOW]:
            task_json = self.r.rpop(queue)
            if task_json:
                task = json.loads(task_json)
                # 移到处理中队列
                self.r.hset(QUEUE_PROCESSING, task["id"], task_json)
                return task
        
        return None
    
    def complete_task(self, task_id: str, result: dict = None):
        """完成任务"""
        task_json = self.r.hget(QUEUE_PROCESSING, task_id)
        if task_json:
            task = json.loads(task_json)
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            self.r.hdel(QUEUE_PROCESSING, task_id)
            self.r.lpush(QUEUE_COMPLETED, json.dumps(task))
            self.r.incr(STATS_SUCCESS)
            print(f"✅ 任务完成: {task_id}")
            return True
        return False
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        task_json = self.r.hget(QUEUE_PROCESSING, task_id)
        if task_json:
            task = json.loads(task_json)
            task["error"] = error
            task["failed_at"] = datetime.now().isoformat()
            task["retry_count"] = task.get("retry_count", 0) + 1
            
            if task["retry_count"] < task.get("max_retries", 3):
                # 重试
                print(f"🔄 任务重试: {task_id} (第{task['retry_count']}次)")
                self.add_task(task, task.get("priority", "normal"), delay=5)
            else:
                # 永久失败
                self.r.hdel(QUEUE_PROCESSING, task_id)
                self.r.lpush(QUEUE_FAILED, json.dumps(task))
                self.r.incr(STATS_FAILED)
                print(f"❌ 任务失败: {task_id}")
            
            return True
        return False
    
    def get_stats(self):
        """获取队列统计"""
        return {
            "high": self.r.llen(QUEUE_HIGH),
            "normal": self.r.llen(QUEUE_NORMAL),
            "low": self.r.llen(QUEUE_LOW),
            "delay": self.r.zcard(QUEUE_DELAY),
            "processing": self.r.hlen(QUEUE_PROCESSING),
            "completed": self.r.llen(QUEUE_COMPLETED),
            "failed": self.r.llen(QUEUE_FAILED),
            "total": int(self.r.get(STATS_TOTAL) or 0),
            "success": int(self.r.get(STATS_SUCCESS) or 0),
            "failed_total": int(self.r.get(STATS_FAILED) or 0)
        }
    
    def get_completed_tasks(self, limit: int = 50):
        """获取已完成任务"""
        tasks = []
        for item in self.r.lrange(QUEUE_COMPLETED, 0, limit - 1):
            tasks.append(json.loads(item))
        return tasks
    
    def get_failed_tasks(self, limit: int = 50):
        """获取失败任务"""
        tasks = []
        for item in self.r.lrange(QUEUE_FAILED, 0, limit - 1):
            tasks.append(json.loads(item))
        return tasks
    
    def retry_failed(self, task_id: str = None):
        """重试失败任务"""
        if task_id:
            # 重试特定任务
            tasks = self.get_failed_tasks(100)
            for task in tasks:
                if task["id"] == task_id:
                    self.add_task(task, task.get("priority", "normal"))
                    # 从失败队列移除
                    self.r.lrem(QUEUE_FAILED, 1, json.dumps(task))
                    return True
        else:
            # 重试所有失败任务
            tasks = self.get_failed_tasks(1000)
            for task in tasks:
                self.add_task(task, task.get("priority", "normal"))
                self.r.lrem(QUEUE_FAILED, 1, json.dumps(task))
            return len(tasks)
        return False
    
    def clear_all(self):
        """清空所有队列（危险操作）"""
        for key in [QUEUE_HIGH, QUEUE_NORMAL, QUEUE_LOW, QUEUE_DELAY, 
                    QUEUE_PROCESSING, QUEUE_COMPLETED, QUEUE_FAILED]:
            self.r.delete(key)
        self.r.delete(STATS_TOTAL, STATS_SUCCESS, STATS_FAILED)
        print("🗑️ 所有队列已清空")

# HTTP API 服务
from http.server import HTTPServer, BaseHTTPRequestHandler

queue = RedisTaskQueue()

class QueueHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/queue/stats':
            self.send_json(queue.get_stats())
        elif self.path == '/api/queue/completed':
            self.send_json({"tasks": queue.get_completed_tasks()})
        elif self.path == '/api/queue/failed':
            self.send_json({"tasks": queue.get_failed_tasks()})
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/queue/add':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            task_id = queue.add_task(
                task={"type": data.get("type"), "prompt": data.get("prompt")},
                priority=data.get("priority", "normal"),
                delay=data.get("delay", 0)
            )
            self.send_json({"success": True, "task_id": task_id})
        
        elif self.path == '/api/queue/retry':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            result = queue.retry_failed(data.get("task_id"))
            self.send_json({"success": True, "retried": result})
        
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        pass

# 工作进程
def worker_loop():
    """工作进程主循环"""
    print("🚀 Redis 工作进程启动，等待任务...")
    
    while True:
        task = queue.get_task(timeout=5)
        if task:
            task_type = task.get("type", "unknown")
            prompt = task.get("prompt", "")
            
            print(f"🔧 处理任务: {task['id']} (类型: {task_type})")
            
            try:
                # 根据任务类型执行
                if task_type == "chat":
                    import subprocess
                    result = subprocess.run(
                        f'openclaw infer model run --model ollama/qwen2.5:3b --prompt "{prompt}"',
                        shell=True, capture_output=True, text=True, timeout=60
                    )
                    queue.complete_task(task["id"], {"output": result.stdout})
                
                elif task_type == "code":
                    result = subprocess.run(
                        f'openclaw agent --agent engineer -m "{prompt}"',
                        shell=True, capture_output=True, text=True, timeout=60
                    )
                    queue.complete_task(task["id"], {"output": result.stdout})
                
                else:
                    queue.complete_task(task["id"], {"result": "done"})
                    
            except subprocess.TimeoutExpired:
                queue.fail_task(task["id"], "Timeout")
            except Exception as e:
                queue.fail_task(task["id"], str(e))
        
        time.sleep(1)

if __name__ == "__main__":
    import threading
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "worker":
            worker_loop()
        elif sys.argv[1] == "stats":
            print(json.dumps(queue.get_stats(), indent=2))
        elif sys.argv[1] == "clear":
            queue.clear_all()
    else:
        # 启动工作进程
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
        
        # 启动 HTTP API
        port = 8091
        print(f"📊 Redis 队列 API: http://localhost:{port}")
        HTTPServer(("0.0.0.0", port), QueueHandler).serve_forever()
