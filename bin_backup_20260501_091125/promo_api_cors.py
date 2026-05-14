#!/usr/bin/env python3
import json, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler

def make_promo(city, style):
    time.sleep(1)
    print(f"✅ {city}{style} 宣传片制作完成")

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/promo/make':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            threading.Thread(target=make_promo, args=(body.get('city','香港'), body.get('style','科技'))).start()
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "🎬 开始制作"}).encode())
    
    def log_message(self, format, *args): pass

print("🎬 宣传片 API (CORS修复): http://localhost:8086")
HTTPServer(("0.0.0.0", 8086), Handler).serve_forever()
