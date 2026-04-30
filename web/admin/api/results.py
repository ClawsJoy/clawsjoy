#!/usr/bin/env python3
import sqlite3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "/home/flybo/.openclaw/task_results.db"
QUEUE_DIR = "/tmp/tenants/queue"

class ResultHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/results":
            conn = sqlite3.connect(DB_PATH)
            conn.text_factory = bytes
            c = conn.cursor()
            c.execute("SELECT id, tenant, task_type, city, status, output, created_at FROM task_results ORDER BY id DESC LIMIT 100")
            rows = c.fetchall()
            conn.close()

            def safe(v):
                return v.decode('utf-8', errors='ignore') if isinstance(v, bytes) else str(v)

            results = []
            for r in rows:
                results.append({
                    "id": r[0],
                    "tenant": safe(r[1]),
                    "task_type": safe(r[2]),
                    "city": safe(r[3]),
                    "status": safe(r[4]),
                    "output": safe(r[5])[:200],
                    "created_at": safe(r[6])
                })
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/retry_task":
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            task_file = os.path.join(QUEUE_DIR, f"retry_{data['id']}.json")
            with open(task_file, 'w') as f:
                json.dump({
                    "tenant": data['tenant'],
                    "task_type": data['task_type'],
                    "city": data['city']
                }, f)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    os.makedirs(QUEUE_DIR, exist_ok=True)
    print("📊 结果API启动（支持重试）: http://localhost:8085/api/results")
    HTTPServer(("0.0.0.0", 8085), ResultHandler).serve_forever()
