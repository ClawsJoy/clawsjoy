#!/usr/bin/env python3
"""Promo API - 工作版本"""

import json
import time
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8108
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/promo/make':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            city = data.get('city', data.get('topic', '香港'))
            
            video_name = f"promo_{city}_{int(time.time())}.mp4"
            video_path = VIDEO_DIR / video_name
            
            cmd = f'ffmpeg -f lavfi -i color=c=blue:s=1920x1080:d=5 -vf "drawtext=text=\'{city}宣传片\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" -y "{video_path}"'
            subprocess.run(cmd, shell=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = {"success": True, "video_url": f"/videos/{video_name}", "duration": 5, "has_audio": False}
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    print(f"🎬 Promo API on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
