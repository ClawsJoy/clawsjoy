#!/usr/bin/env python3
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

REVIEW_FILE = os.path.expanduser('~/.openclaw/web/review/data.json')

class SubmitHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/submit':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            # 读取现有数据
            if os.path.exists(REVIEW_FILE):
                with open(REVIEW_FILE, 'r') as f:
                    reviews = json.load(f)
            else:
                reviews = []
            
            # 添加新任务
            reviews.append({
                'id': int(datetime.now().timestamp() * 1000),
                'title': data.get('title'),
                'content': data.get('content'),
                'submitter': data.get('submitter'),
                'submitTime': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'pending'
            })
            
            # 保存
            with open(REVIEW_FILE, 'w') as f:
                json.dump(reviews, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 8085
    server = HTTPServer(('localhost', port), SubmitHandler)
    print(f'Submit API running on port {port}')
    server.serve_forever()
