#!/usr/bin/env python3
"""修复版 Chat API"""

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        
        # 提取城市
        topic = "香港"
        for city in ["香港", "上海", "深圳", "北京"]:
            if city in user_input:
                topic = city
                break
        
        print(f"📥 收到: {user_input[:50]}...")
        
        # 调用 Promo API
        try:
            resp = requests.post("http://localhost:8108/api/promo/make",
                                json={"topic": topic, "duration": 30},
                                timeout=120)
            result = resp.json()
            print(f"✅ Promo API 返回: {result.get('success')}")
            
            if result.get("success"):
                video_url = result.get("video_url")
                self._send_json({"type": "result", "message": "✅ 视频已生成", "data": {"video_url": video_url}})
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
    print(f"🤖 Chat API 修复版启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
