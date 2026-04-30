#!/usr/bin/env python3
"""
JOY Mate 审核系统后端 API
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

REVIEW_FILE = os.path.expanduser('~/.openclaw/web/review/data.json')

def load_data():
    if os.path.exists(REVIEW_FILE):
        with open(REVIEW_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(REVIEW_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def notify_agent(agent, message):
    """通知 Agent"""
    try:
        subprocess.run(
            ['openclaw', 'agent', '--agent', agent, '-m', message],
            timeout=10,
            capture_output=True
        )
        print(f"通知 {agent}: {message}")
    except Exception as e:
        print(f"通知失败: {e}")

class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/review/list':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(load_data()).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/review/approve':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            task_id = data.get('id')
            feedback = data.get('feedback', '')
            
            reviews = load_data()
            for review in reviews:
                if review.get('id') == task_id:
                    review['status'] = 'approved'
                    review['reviewed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    review['feedback'] = feedback
                    
                    # 通知对应的 Agent
                    if review.get('submitter') == 'engineer':
                        notify_agent('engineer', f'✅ 后端 API 已通过审核。请部署到测试环境：cd ~/joymate_api && python app.py')
                    elif review.get('submitter') == 'designer':
                        notify_agent('designer', f'✅ UI 设计已通过审核。请准备前端页面，对接后端 API。')
                    break
            
            save_data(reviews)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        
        elif self.path == '/api/review/reject':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            task_id = data.get('id')
            feedback = data.get('feedback', '')
            
            reviews = load_data()
            for review in reviews:
                if review.get('id') == task_id:
                    review['status'] = 'rejected'
                    review['reviewed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    review['feedback'] = feedback
                    
                    # 通知对应的 Agent
                    if review.get('submitter') == 'engineer':
                        notify_agent('engineer', f'❌ 后端 API 被驳回。原因：{feedback}，请修改后重新提交。')
                    elif review.get('submitter') == 'designer':
                        notify_agent('designer', f'❌ UI 设计被驳回。原因：{feedback}，请修改后重新提交。')
                    break
            
            save_data(reviews)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 8086
    server = HTTPServer(('localhost', port), ReviewHandler)
    print(f'审核 API 运行在端口 {port}')
    server.serve_forever()
