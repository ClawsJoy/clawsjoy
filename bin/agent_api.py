#!/usr/bin/env python3
"""Agent API - 简化稳定版"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 18103

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "agent-api"}).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": "ok", "received": True}).encode())

if __name__ == '__main__':
    print(f"🤖 Agent API 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
