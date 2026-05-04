#!/usr/bin/env python3
"""Agent 模式 v2 - 更智能的意图识别 + 闲聊回退"""
import json
import requests
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://redis:11434/api/generate"
OLLAMA_MODEL = "phi:2.7b"  # 小模型，更快

class AgentHandler(BaseHTTPRequestHandler):
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
    
    def _is_promo(self, text):
        """更宽松的宣传片检测"""
        patterns = [
            r'(制作|生成|做|create|make).{0,3}(宣传片|宣傳片|promo)',
            r'(宣传片|宣傳片).{0,3}(制作|生成)',
            r'生产片', r'產片', r'宣傳', r'宣传'
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_city(self, text):
        cities = ['香港', '北京', '上海', '深圳', '广州', '杭州', '成都']
        for city in cities:
            if city in text:
                return city
        return '香港'
    
    def _call_ollama(self, prompt, max_tokens=50):
        try:
            resp = requests.post(OLLAMA_API,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.7}
                },
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json().get('response', '')
        except Exception as e:
            print(f"Ollama 错误: {e}")
        return None
    
    def _handle_agent(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            user_input = data.get('message', '')
            
            print(f"📝 用户: {user_input}", flush=True)
            
            # 1. 宣传片检测（宽松）
            if self._is_promo(user_input):
                city = self._extract_city(user_input)
                print(f"🎬 触发宣传片: {city}")
                resp = requests.post("http://redis:8084/api/task/promo",
                                    json={'city': city, 'style': '科技', 'tenant_id': '1'},
                                    timeout=60)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get('success'):
                        self.send_json({'type': 'promo', 'video_url': result.get('video_url')})
                        return
                self.send_json({'type': 'text', 'message': f'生成{city}宣传片失败'})
                return
            
            # 2. 照片查询
            if any(k in user_input for k in ['照片', '图片', '相册', '我的照片', '找照片']):
                print(f"📁 查询照片")
                resp = requests.get("http://redis:8084/api/library/list", 
                                   params={'tenant_id': '1', 'limit': 5})
                if resp.status_code == 200:
                    files = resp.json().get('files', [])
                    if files:
                        names = [f['name'] for f in files[:5]]
                        self.send_json({'type': 'text', 'message': f'📁 你有 {len(files)} 个文件: ' + ', '.join(names)})
                        return
                self.send_json({'type': 'text', 'message': '暂无照片'})
                return
            
            # 3. 普通聊天（调用 AI）
            print(f"💬 调用 AI 闲聊")
            reply = self._call_ollama(user_input, max_tokens=80)
            if reply:
                # 限制回复长度
                if len(reply) > 150:
                    reply = reply[:150] + '...'
                self.send_json({'type': 'text', 'message': reply})
            else:
                self.send_json({'type': 'text', 'message': '你好！有什么可以帮你的？'})
            
        except Exception as e:
            print(f"错误: {e}", flush=True)
            self.send_json({'type': 'text', 'message': '服务异常，请稍后'})
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    port = 8087
    print(f"🤖 Agent v2 运行中: http://redis:{port}")
    HTTPServer(('0.0.0.0', port), AgentHandler).serve_forever()
