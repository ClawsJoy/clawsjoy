#!/usr/bin/env python3
"""Agent - 根据输入语言自动切换模型"""
import json
import requests
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://redis:11434/api/generate"
MODEL_ZH = "qwen2.5:3b"   # 中文模型
MODEL_EN = "phi:2.7b"      # 英文模型（快）

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
    
    def _detect_language(self, text):
        """检测语言：返回 'zh' 或 'en'"""
        # 统计中文字符比例
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > len(text) * 0.1:  # 超过10%中文字符
            return 'zh'
        return 'en'
    
    def _is_promo(self, text):
        patterns = [
            r'(制作|生成|做).{0,3}(宣传片|宣傳片)',
            r'make.*promo', r'create.*video', r'generate.*promo'
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_city(self, text):
        cities = ['香港', '北京', '上海', '深圳', 'Hong Kong', 'Beijing', 'Shanghai', 'Shenzhen']
        for city in cities:
            if city in text:
                if city in ['Hong Kong', 'Beijing', 'Shanghai', 'Shenzhen']:
                    return {'Hong Kong': '香港', 'Beijing': '北京', 'Shanghai': '上海', 'Shenzhen': '深圳'}.get(city, '香港')
                return city
        return '香港'
    
    def _is_photo_query(self, text):
        keywords = ['照片', '图片', '相册', 'photo', 'picture', 'image']
        return any(k in text.lower() for k in keywords)
    
    def _call_ollama(self, prompt, lang):
        """根据语言调用对应模型"""
        model = MODEL_ZH if lang == 'zh' else MODEL_EN
        print(f"   🤖 使用模型: {model}", flush=True)
        
        try:
            resp = requests.post(OLLAMA_API,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100, "temperature": 0.8}
                },
                timeout=30
            )
            if resp.status_code == 200:
                reply = resp.json().get('response', '')
                if len(reply) > 200:
                    reply = reply[:200] + '...'
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
            
            # 检测语言
            lang = self._detect_language(user_input)
            print(f"🌐 检测语言: {'中文' if lang == 'zh' else '英文'}", flush=True)
            
            # 1. 宣传片任务
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
                msg = f'生成{city}宣传片失败' if lang == 'zh' else f'Failed to generate promo for {city}'
                self.send_json({'type': 'text', 'message': msg})
                return
            
            # 2. 照片查询
            if self._is_photo_query(user_input):
                print(f"📁 查询照片")
                resp = requests.get("http://redis:8084/api/library/list", 
                                   params={'tenant_id': '1', 'limit': 5})
                if resp.status_code == 200:
                    files = resp.json().get('files', [])
                    if files:
                        names = [f['name'] for f in files[:5]]
                        msg = f'📁 文件: ' + ', '.join(names)
                        self.send_json({'type': 'text', 'message': msg})
                        return
                msg = '暂无照片' if lang == 'zh' else 'No photos found'
                self.send_json({'type': 'text', 'message': msg})
                return
            
            # 3. 普通聊天（切换模型）
            print(f"💬 聊天回复")
            reply = self._call_ollama(user_input, lang)
            if reply:
                self.send_json({'type': 'text', 'message': reply})
            else:
                default = '你好！有什么可以帮你的？' if lang == 'zh' else 'Hello! How can I help you?'
                self.send_json({'type': 'text', 'message': default})
            
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
    print(f"🤖 智能切换 Agent: http://redis:{port}")
    print(f"   - 中文 → {MODEL_ZH}")
    print(f"   - 英文 → {MODEL_EN}")
    HTTPServer(('0.0.0.0', port), AgentHandler).serve_forever()
