#!/usr/bin/env python3
"""
代理服务器 - 监听 9000 端口，将 /api/* 请求转发到 8084
"""

import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            url = f"http://localhost:8084{self.path}"
            try:
                with urllib.request.urlopen(url, timeout=30) as resp:
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            req = urllib.request.Request(
                f"http://localhost:8084{self.path}", data=body, method="POST"
            )
            req.add_header("Content-Type", self.headers.get("Content-Type", ""))
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = 9001
    print(f"API Proxy on http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), ProxyHandler).serve_forever()
