#!/usr/bin/env python3
import json
import requests
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

TASK_API = "http://redis:8084"
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
    
    def _is_promo(self, msg):
        """严格检测宣传片相关关键词"""
        keywords = ['宣传片', '宣傳片', 'promo', '宣传视频', '宣傳視頻', '製作宣傳', '制作宣传', '做宣传', '做宣傳']
        for kw in keywords:
            if kw in msg:
                return True
        # 检测模式：“做XX宣传片”、“制作XX宣传片”
        if re.search(r'(做|制作|生成).{0,5}(宣传片|宣傳片)', msg):
            return True
        return False
    
    def _extract_city(self, msg):
        cities = ['香港', '北京', '上海', '深圳', '广州', '杭州', '成都', '重庆', '武汉']
        for city in cities:
            if city in msg:
                return city
        return '香港'
    
    def _is_photo_query(self, msg):
        return any(k in msg for k in ['照片', '图片', '相册', '我的照片', '找照片'])
    
    def _call_ollama(self, prompt):
        """只用于闲聊"""
        try:
            resp = requests.post(OLLAMA_API, 
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 50, "temperature": 0.8}
                },
                timeout=20
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
            tenant_id = data.get('tenant_id', '1')
            message = data.get('message', '')
            
            print(f"收到: {message}", flush=True)
            
            # 1. 宣传片（最高优先级）
            if self._is_promo(message):
                city = self._extract_city(message)
                print(f"🎬 触发宣传片: {city}", flush=True)
                resp = requests.post(f"{TASK_API}/api/task/promo", 
                                    json={'city': city, 'style': '科技', 'tenant_id': tenant_id},
                                    timeout=60)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get('success'):
                        self.send_json({'type': 'promo', 'video_url': result.get('video_url')})
                        return
                self.send_json({'type': 'text', 'message': f'生成{city}宣传片失败'})
                return
            
            # 2. 照片查询
            if self._is_photo_query(message):
                resp = requests.get(f"{TASK_API}/api/library/list", params={'tenant_id': tenant_id, 'limit': 5})
                if resp.status_code == 200:
                    files = resp.json().get('files', [])
                    if files:
                        names = [f['name'] for f in files[:5]]
                        self.send_json({'type': 'text', 'message': f'📁 资料库: ' + ', '.join(names)})
                        return
                self.send_json({'type': 'text', 'message': '暂无照片'})
                return
            
            # 3. 普通闲聊（交给 AI）
            ai_reply = self._call_ollama(message)
            if ai_reply:
                self.send_json({'type': 'text', 'message': ai_reply[:150]})
            else:
                self.send_json({'type': 'text', 'message': '你可以说"制作北京宣传片"或"找我的照片"'})
                
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
    print(f"🚦 路由版 Chat API on http://redis:{port}")
    HTTPServer(('0.0.0.0', port), ChatHandler).serve_forever()
