#!/usr/bin/env python3
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
        print(f"采集错误: {e}")
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
        raw_data = self.rfile.read(length)
        print(f"收到原始数据长度: {len(raw_data)}")
        
        try:
            data = json.loads(raw_data)
        except Exception as e:
            print(f"JSON解析错误: {e}")
            self.send_json({"success": False, "error": "JSON解析失败"})
            return
        
        topic = data.get('topic', '香港')
        script = data.get('script', '')
        
        print(f"🎬 主题: {topic}")
        print(f"📝 脚本长度: {len(script)}")
        print(f"📝 脚本前100字: {script[:100] if script else '(空)'}")
        
        if len(script) < 50:
            # 脚本太短，使用默认脚本
            script = "香港优才计划2026年迎来重大调整。分数门槛从80分降至75分。新增金融科技、人工智能、数据科学人才清单。审批时间从6个月缩短至3个月。"
            print(f"⚠️ 使用默认脚本，长度: {len(script)}")
        
        images = fetch_images("Hong Kong", 12)
        if not images:
            self.send_json({"success": False, "error": "No images"})
            return
        
        video_name = f"hk_{int(time.time())}.mp4"
        video_path = VIDEO_DIR / video_name
        
        # 根据脚本长度决定视频时长
        duration = max(10, min(180, len(script) / 10))
        print(f"⏱️ 视频时长: {duration} 秒")
        
        cmd = f'ffmpeg -loop 1 -i "{images[0]}" -c:v libx264 -t {duration} -pix_fmt yuv420p -y "{video_path}"'
        subprocess.run(cmd, shell=True)
        
        self.send_json({"success": True, "video_url": f"/videos/{video_name}", "image_count": len(images), "duration": duration})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"🎬 Promo API (调试版) on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
