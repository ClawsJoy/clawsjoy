#!/usr/bin/env python3
"""Promo API - 简化版（无字幕）"""

import json
import os
import uuid
import time
import requests
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

UNSPLASH_KEY = "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs"
PORT = 8105
BASE_DIR = Path("/mnt/d/clawsjoy")
IMAGE_DIR = BASE_DIR / "web/images"
VIDEO_DIR = BASE_DIR / "web/videos"
AUDIO_DIR = BASE_DIR / "web/audio"

for d in [IMAGE_DIR, VIDEO_DIR, AUDIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def fetch_images(keyword, count=10):
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

def generate_tts(script, output_path):
    try:
        resp = requests.post("http://localhost:9000/api/tts", json={"text": script}, timeout=30)
        if resp.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False

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
        script = data.get('script', f"欢迎来到香港，了解{topic}的最新资讯。")
        
        print(f"🎬 生成视频: {topic}")
        print(f"📝 脚本长度: {len(script)} 字符")
        
        images = fetch_images("Hong Kong", 12)
        if not images:
            self.send_json({"success": False, "error": "No images"})
            return
        
        audio_file = AUDIO_DIR / f"tts_{int(time.time())}.mp3"
        has_audio = generate_tts(script, audio_file)
        
        duration = 30
        if has_audio:
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_file)], capture_output=True, text=True)
            try:
                duration = float(result.stdout.strip())
            except:
                duration = 30
        
        video_name = f"hk_{int(time.time())}.mp4"
        video_path = VIDEO_DIR / video_name
        concat_file = VIDEO_DIR / "concat.txt"
        
        per_image = duration / len(images)
        with open(concat_file, 'w') as f:
            for img in images:
                f.write(f"file '{img}'\n")
                f.write(f"duration {per_image}\n")
        
        if has_audio:
            cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -i {audio_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -c:a aac -shortest -pix_fmt yuv420p -y {video_path}'
        else:
            cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -pix_fmt yuv420p -y {video_path}'
        
        subprocess.run(cmd, shell=True)
        os.remove(concat_file)
        if audio_file.exists():
            os.remove(audio_file)
        
        self.send_json({"success": True, "video_url": f"/videos/{video_name}", "image_count": len(images), "duration": duration, "has_audio": has_audio})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"🎬 Promo API on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
