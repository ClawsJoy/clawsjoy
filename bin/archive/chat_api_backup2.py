#!/usr/bin/env python3
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

TASK_API = "http://redis:8084"

class ChatHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            self._handle_chat()
        else:
            self.send_error(404)
    
    def _handle_chat(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get('tenant_id', '1')
            message = data.get('message', '')
            
            print(f"收到消息: {message}", flush=True)
            
            # 更宽松的匹配
            if '宣传片' in message or '宣傳片' in message:
                city = '香港'
                if '北京' in message: city = '北京'
                elif '上海' in message: city = '上海'
                print(f"匹配到宣传片，城市: {city}", flush=True)
                resp = requests.post(f"{TASK_API}/api/task/promo", 
                                    json={'city': city, 'style': '科技', 'tenant_id': tenant_id},
                                    timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get('success'):
                        self.send_json({'type': 'promo', 'video_url': result.get('video_url')})
                        return
                self.send_json({'type': 'text', 'message': f'生成{city}宣传片失败'})
                return
            
            if any(k in message for k in ['照片', '图片', '相册']):
                resp = requests.get(f"{TASK_API}/api/library/list", params={'tenant_id': tenant_id, 'limit': 5})
                if resp.status_code == 200:
                    data = resp.json()
                    files = data.get('files', [])
                    if files:
                        names = [f['name'] for f in files[:5]]
                        self.send_json({'type': 'text', 'message': f'资料库: {", ".join(names)}'})
                        return
                self.send_json({'type': 'text', 'message': '暂无照片'})
                return
            
            self.send_json({'type': 'text', 'message': '试试说“制作北京宣传片”或“找我的照片”。'})
        except Exception as e:
            self.send_json({'type': 'text', 'message': f'错误: {str(e)}'})
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    port = 8087
    print(f"💬 Chat API on http://redis:{port}")
    HTTPServer(('0.0.0.0', port), ChatHandler).serve_forever()
