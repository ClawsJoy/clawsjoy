#!/usr/bin/env python3
"""简化版 Promo API"""

import json
import time
import uuid
import requests
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

UNSPLASH_KEY = "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs"
PORT = 8105
BASE_DIR = Path("/mnt/d/clawsjoy")
IMAGE_DIR = BASE_DIR / "web/images"
VIDEO_DIR = BASE_DIR / "web/videos"

def fetch_images(keyword, count=8):
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": keyword, "per_page": count, "orientation": "landscape"}
    images = []
    try:
        resp = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            for photo in resp.json().get('results', []):
                img_data = requests.get(photo['urls']['regular']).content
                img_path = IMAGE_DIR / f"{uuid.uuid4().hex}.jpg"
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                images.append(str(img_path))
    except Exception as e:
        print(e)
    return images

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_POST(self):
        if self.path != '/api/promo/make':
            self.send_error(404)
            return
        
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        topic = data.get('topic', '香港')
        script = data.get('script', '')
        
        print(f"🎬 生成视频: {topic}, 脚本长度: {len(script)}")
        
        images = fetch_images("Hong Kong", 12)
        if not images:
            self.send_json({"success": False, "error": "No images"})
            return
        
        video_name = f"hk_{int(time.time())}.mp4"
        video_path = VIDEO_DIR / video_name
        
        # 简单单图视频
        cmd = f'ffmpeg -loop 1 -i "{images[0]}" -c:v libx264 -t 30 -pix_fmt yuv420p -y "{video_path}"'
        subprocess.run(cmd, shell=True)
        
        self.send_json({"success": True, "video_url": f"/videos/{video_name}", "image_count": len(images)})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"🎬 Promo API on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
