#!/usr/bin/env python3
"""Chat API - 强制禁用代理"""

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# 强制禁用代理
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.trust_env = False
session.proxies = {"http": None, "https": None}

PORT = 18109

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        user_input = data.get('text', '')
        
        topic = "香港"
        for city in ["香港", "上海", "深圳", "北京"]:
            if city in user_input:
                topic = city
                break
        
        print(f"📥 制作 {topic} 宣传片...")
        
        try:
            # 使用禁用代理的 session
            resp = session.post("http://localhost:8108/api/promo/make",
                               json={"topic": topic, "duration": 30},
                               timeout=120)
            result = resp.json()
            
            if result.get("success"):
                self._send_json({"type": "result", "message": "✅ 视频已生成", "data": {"video_url": result.get("video_url")}})
            else:
                self._send_json({"type": "result", "message": "视频生成失败", "data": result})
        except Exception as e:
            print(f"❌ 错误: {e}")
            self._send_json({"type": "result", "message": f"视频生成失败: {str(e)}"})
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🤖 Chat API (无代理) 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
