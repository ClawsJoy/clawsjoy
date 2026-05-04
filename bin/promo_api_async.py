#!/usr/bin/env python3
"""异步宣传片制作 API - 立即返回，后台执行"""

import subprocess
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

def make_promo_async(city, style):
    """后台执行宣传片制作"""
    time.sleep(1)
    keyword = f"{city}{style}"
    cmd = f"/root/clawsjoy/bin/make_video '{keyword}宣传片' '/root/.openclaw/web/images/{city}/' '/tmp/{keyword}.mp4' '{keyword}'"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ {city}{style} 宣传片制作完成")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/promo/make':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            city = body.get('city', '香港')
            style = body.get('style', '科技')
            
            # 异步执行
            threading.Thread(target=make_promo_async, args=(city, style)).start()
            
            self.send_json({"success": True, "message": f"🎬 开始制作{city}{style}宣传片"})
        else:
            self.send_error(404)
    
    def do_GET(self):
        self.send_json({"status": "ok", "service": "promo_api"})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print("🎬 异步宣传片 API: http://redis:8086")
    HTTPServer(("0.0.0.0", 8086), Handler).serve_forever()
