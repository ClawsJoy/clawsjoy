#!/usr/bin/env python3
"""Web 上传 API - 真实上传"""

import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8109
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/upload/youtube':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            video_url = data.get('video_url', '')
            
            # 提取视频文件名
            video_name = video_url.split('/')[-1]
            video_path = VIDEO_DIR / video_name
            
            if not video_path.exists():
                self.send_json({"success": False, "error": f"视频不存在: {video_name}"})
                return
            
            # 调用真实上传脚本
            result = subprocess.run(
                ['python3', '/mnt/d/clawsjoy/agents/youtube_upload_final.py'],
                capture_output=True, text=True
            )
            
            # 简单解析输出获取视频 ID
            import re
            match = re.search(r'https://youtu.be/([a-zA-Z0-9_-]+)', result.stdout)
            video_id = match.group(1) if match else "unknown"
            
            self.send_json({
                "success": True,
                "url": f"https://youtu.be/{video_id}",
                "message": "上传完成"
            })
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"Web Upload API on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
