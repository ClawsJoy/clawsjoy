#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/coffee/shops":
            self.send_json({
                "success": True,
                "shops": [
                    {"id": 1, "name": "星巴克", "menu": {"拿铁": 28, "美式": 22}},
                    {"id": 2, "name": "瑞幸", "menu": {"生椰拿铁": 25, "厚乳拿铁": 26}}
                ]
            })
        else:
            self.send_json({"error": "not found"}, 404)
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8085), Handler).serve_forever()
