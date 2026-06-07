#!/usr/bin/env python3
"""简单的全景图服务器，支持动态列表"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class PanoramaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/list-panoramas":
            downloads = Path("downloads")
            files = []
            if downloads.exists():
                files = sorted(
                    [f"downloads/{f.name}" for f in downloads.glob("panorama_*.png")],
                    reverse=True,
                )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"files": files}).encode())
            return

        # 处理普通文件
        return super().do_GET()


if __name__ == "__main__":
    port = 8888
    print(f"Starting panorama server on port {port}")
    print(f"Open http://localhost:{port}/panorama_viewer.html")
    HTTPServer(("0.0.0.0", port), PanoramaHandler).serve_forever()
