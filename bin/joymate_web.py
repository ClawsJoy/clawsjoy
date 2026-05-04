#!/usr/bin/env python3
"""
Joy Mate 独立 Web 服务
端口: 3000
不依赖 OpenClaw Canvas
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path

WEB_DIR = Path("/root/clawsjoy/web/joymate")

class JoyMateHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    
    def log_message(self, format, *args):
        print(f"[JoyMate] {format % args}")

if __name__ == "__main__":
    port = 3000
    print(f"🦞 Joy Mate Web 服务启动: http://redis:{port}")
    print(f"   访问地址: http://redis:{port}/index.html")
    HTTPServer(("0.0.0.0", port), JoyMateHandler).serve_forever()
