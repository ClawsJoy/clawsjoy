#!/usr/bin/env python3
"""极简版本 - 只做一件事：调用 Promo API"""

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
        
        # 简单提取城市
        topic = "香港"
        for city in ["香港", "上海", "深圳", "北京"]:
            if city in user_input:
                topic = city
                break
        
        # 调用 Promo API
        try:
            resp = requests.post("http://localhost:8108/api/promo/make",
                                json={"topic": topic, "duration": 30},
                                timeout=120)
            result = resp.json() if resp.status_code == 200 else {"success": False}
        except Exception as e:
            result = {"success": False, "error": str(e)}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
