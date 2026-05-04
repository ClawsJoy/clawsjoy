#!/usr/bin/env python3
"""Joy Mate 任务提交 API。

负责接收任务并写入队列目录，供后续任务执行器消费。
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from settings import TASK_QUEUE_DIR, PORT_TASK
from py_logging import get_logger

TASKS_DIR = TASK_QUEUE_DIR
TASKS_DIR.mkdir(parents=True, exist_ok=True)
LOGGER = get_logger("task_api")

class TaskHandler(BaseHTTPRequestHandler):
    """任务相关 HTTP 处理器。"""

    def do_POST(self):
        """处理任务提交接口。"""
        if self.path == "/api/task/submit":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            tenant_id = data.get('tenant_id', 1)
            task_type = data.get('task_type', 'promo')
            params = data.get('params', {})
            
            # 任务文件是队列协议的一部分，字段需保持稳定。
            task = {
                "tenant_id": tenant_id,
                "task_type": task_type,
                "params": params,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # 通过时间戳 + tenant 生成文件名，减少冲突概率。
            task_file = TASKS_DIR / f"task_{int(time.time())}_{tenant_id}.json"
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "task_id": task_file.name}).encode())
    
    def do_GET(self):
        """处理轻量状态查询接口。"""
        if self.path == "/api/task/status":
            tenant_id = self.headers.get('X-Tenant-Id', '1')
            # 简单返回
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "tenant": tenant_id}).encode())
    
    def log_message(self, format, *args):
        """记录标准访问日志。"""
        LOGGER.info(format % args)

if __name__ == "__main__":
    port = PORT_TASK
    LOGGER.info("Task API started: http://redis:%s", port)
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()
