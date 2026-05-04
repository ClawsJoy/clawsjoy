#!/usr/bin/env python3
import json
import requests
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://redis:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"  # 换回中文模型

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
        patterns = [r'(制作|生成|做).{0,3}(宣传片|宣傳片)', r'生产片', r'產片', r'宣傳']
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
    
    def _call_ollama(self, prompt):
        try:
            # 强制要求中文回复
            full_prompt = f"请用中文简短回复（20字以内）：{prompt}"
            resp = requests.post(OLLAMA_API,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"num_predict": 40, "temperature": 0.5}
                },
                timeout=30
            )
            if resp.status_code == 200:
                reply = resp.json().get('response', '')
                # 如果回复是英文，返回默认中文
                if reply and not re.search(r'[\u4e00-\u9fff]', reply):
                    return "你好！有什么可以帮你的？"
                if len(reply) > 100:
                    reply = reply[:100] + '...'
                return reply
        except Exception as e:
            print(f"Ollama 错误: {e}")
        return None
    
    def _handle_agent(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            user_input = data.get('message', '')
            
            print(f"📝 用户: {user_input}", flush=True)
            
            if self._is_promo(user_input):
                city = self._extract_city(user_input)
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
            
            if any(k in user_input for k in ['照片', '图片', '相册', '我的照片']):
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
            
            reply = self._call_ollama(user_input)
            if reply:
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
    print(f"🤖 Agent 中文版: http://redis:{port}")
    HTTPServer(('0.0.0.0', port), AgentHandler).serve_forever()
