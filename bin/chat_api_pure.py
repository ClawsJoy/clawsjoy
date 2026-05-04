#!/usr/bin/env python3
"""纯聊天服务 - 只负责 AI 对话"""
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://redis:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

class ChatHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            self._handle_chat()
        else:
            self.send_error(404)
    
    def _call_ollama(self, prompt):
        try:
            resp = requests.post(OLLAMA_API, 
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 60, "temperature": 0.8}
                },
                timeout=25
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
        except Exception as e:
            print(f"Ollama 错误: {e}")
        return None
    
    def _handle_chat(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            message = data.get('message', '')
            print(f"聊天: {message}", flush=True)
            
            reply = self._call_ollama(message)
            if reply:
                self.send_json({'type': 'text', 'message': reply[:200]})
            else:
                self.send_json({'type': 'text', 'message': '你好！有什么可以帮你的？'})
        except Exception as e:
            self.send_json({'type': 'text', 'message': f'服务异常'})
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    port = 8089
    print(f"💬 纯聊天服务 on http://redis:{port}")
    HTTPServer(('0.0.0.0', port), ChatHandler).serve_forever()
