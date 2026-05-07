#!/usr/bin/env python3
"""Chat API Agent - 连接本地 Ollama"""

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/agent':
            self._handle_agent()
        else:
            self.send_error(404)

    def _handle_agent(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            user_input = data.get('text', data.get('message', ''))
            
            print(f"📝 用户: {user_input}")
            
            # 调用本地 Ollama
            resp = requests.post(OLLAMA_API, 
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": user_input,
                    "stream": False,
                    "options": {"num_predict": 500, "temperature": 0.7}
                },
                timeout=60)
            
            if resp.status_code == 200:
                reply = resp.json().get('response', '')
                print(f"🤖 回复: {reply[:100]}...")
                self.send_json({'type': 'text', 'message': reply})
            else:
                print(f"Ollama 返回错误: {resp.status_code}")
                self.send_json({'type': 'text', 'message': '服务暂时不可用'})
        except Exception as e:
            print(f"错误: {e}")
            self.send_json({'type': 'text', 'message': f'服务异常: {str(e)}'})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    PORT = 18101
    print(f"🤖 Chat API 启动在端口 {PORT}")
    print(f"📍 Ollama API: {OLLAMA_API}")
    print(f"📍 使用模型: {OLLAMA_MODEL}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
