#!/usr/bin/env python3
"""任务调度器 API - 负责租户隔离、计费、队列"""

import json
import urllib.request
import sqlite3
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 配置
DB_PATH = "/home/flybo/clawsjoy/data/tasks.db"
PROMO_API = "http://localhost:8086/api/promo/make"

def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tenant_id TEXT,
                  task_type TEXT,
                  params TEXT,
                  status TEXT,
                  result TEXT,
                  created_at TIMESTAMP,
                  completed_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS billing
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tenant_id TEXT,
                  task_type TEXT,
                  amount REAL,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

class TaskHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_json({'status': 'ok', 'service': 'task_api'})
        elif self.path.startswith('/api/task/balance'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            tenant_id = params.get('tenant_id', ['1'])[0]
            balance = self._get_balance(tenant_id)
            self.send_json({'tenant_id': tenant_id, 'balance': balance})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/task/promo':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                tenant_id = data.get('tenant_id', '1')
                city = data.get('city', '香港')
                style = data.get('style', '科技')
                
                print(f"📋 收到任务: tenant={tenant_id}, city={city}, style={style}")
                
                # 1. 记录任务
                task_id = self._record_task(tenant_id, 'promo', {'city': city, 'style': style})
                print(f"✅ 任务记录: task_id={task_id}")
                
                # 2. 扣费
                self._deduct_balance(tenant_id, 0.01)
                print(f"💰 扣费完成: tenant={tenant_id}")
                
                # 3. 调用宣传片 API
                promo_data = json.dumps({'city': city, 'style': style}).encode()
                req = urllib.request.Request(PROMO_API, data=promo_data, method='POST')
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = resp.read().decode()
                print(f"🎬 宣传片 API 调用成功")
                
                # 4. 更新任务状态
                self._update_task(task_id, 'completed', result)
                
                # 5. 返回结果
                result_json = json.loads(result)
                self.send_json({
                    'success': True,
                    'task_id': task_id,
                    'message': f'{city}{style}宣传片已生成',
                    'video_url': result_json.get('video_url', '')
                })
                print(f"✅ 任务完成: task_id={task_id}")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                self.send_json({'success': False, 'error': str(e)}, 500)
        else:
            self.send_error(404)

    def _record_task(self, tenant_id, task_type, params):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO tasks (tenant_id, task_type, params, status, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (tenant_id, task_type, json.dumps(params), 'pending', datetime.now().isoformat()))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def _update_task(self, task_id, status, result):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE tasks SET status=?, result=?, completed_at=?
                     WHERE id=?''',
                  (status, result, datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()

    def _deduct_balance(self, tenant_id, amount):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO billing (tenant_id, task_type, amount, created_at)
                     VALUES (?, ?, ?, ?)''',
                  (tenant_id, 'promo', -amount, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _get_balance(self, tenant_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COALESCE(SUM(amount), 0) FROM billing WHERE tenant_id=?', (tenant_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {format % args}")

if __name__ == '__main__':
    init_db()
    port = 8084
    print(f"📋 Task API started: http://localhost:{port}")
    print(f"  POST /api/task/promo - 提交宣传片任务")
    print(f"  GET /api/task/balance - 查询余额")
    print(f"  GET /health - 健康检查")
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()
