#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

print("启动测试服务 on 8105")
HTTPServer(('0.0.0.0', 8105), H).serve_forever()
