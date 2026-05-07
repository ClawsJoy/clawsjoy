#!/usr/bin/env python3
"""Promo API - 升级版（真实图片 + 基础音频）"""

import json
import os
import time
import uuid
import requests
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8108
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")
IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

def fetch_real_images(keyword, count=5):
    """从 Unsplash 采集真实图片"""
    API_KEY = "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs"
    images = []
    try:
        url = f"https://api.unsplash.com/search/photos"
        params = {"query": keyword, "per_page": count, "orientation": "landscape"}
        headers = {"Authorization": f"Client-ID {API_KEY}"}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            for photo in resp.json().get('results', []):
                img_url = photo['urls']['regular']
                img_data = requests.get(img_url, timeout=30).content
                img_name = f"{uuid.uuid4().hex}.jpg"
                img_path = IMAGE_DIR / img_name
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                images.append(str(img_path))
        print(f"📸 采集到 {len(images)} 张图片")
    except Exception as e:
        print(f"图片采集失败: {e}")
    return images

def generate_simple_audio(text, output_path):
    """生成简单音频（使用 edge-tts）"""
    try:
        cmd = f'edge-tts --text "{text}" --write-media {output_path} --voice zh-CN-XiaoxiaoNeural'
        subprocess.run(cmd, shell=True, timeout=60)
        return output_path.exists() and output_path.stat().st_size > 1000
    except:
        return False

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
            topic = data.get('topic', data.get('city', '香港'))
            duration = data.get('duration', 30)
            
            # 1. 采集真实图片
            images = fetch_real_images(topic, min(10, max(3, duration // 5)))
            
            # 2. 生成文案和音频
            script = data.get('script', f"{topic}科技宣传片，展现城市魅力。")
            audio_path = Path(f"/tmp/audio_{int(time.time())}.mp3")
            has_audio = generate_simple_audio(script, audio_path)
            
            # 3. 生成视频
            video_name = f"promo_{topic}_{int(time.time())}.mp4"
            video_path = VIDEO_DIR / video_name
            
            if images:
                # 多图轮播
                concat_file = Path(f"/tmp/concat_{int(time.time())}.txt")
                per_img = max(2, duration / len(images))
                with open(concat_file, 'w') as f:
                    for img in images:
                        f.write(f"file '{img}'\n")
                        f.write(f"duration {per_img}\n")
                
                if has_audio:
                    cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -i {audio_path} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -c:a aac -shortest -y "{video_path}"'
                else:
                    cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -y "{video_path}"'
                subprocess.run(cmd, shell=True)
                concat_file.unlink()
            else:
                # 无图片时的降级方案
                cmd = f'ffmpeg -f lavfi -i color=c=blue:s=1920x1080:d={duration} -vf "drawtext=text=\'{topic}宣传片\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" -y "{video_path}"'
                subprocess.run(cmd, shell=True)
            
            # 清理临时文件
            for img in images:
                Path(img).unlink()
            if audio_path.exists():
                audio_path.unlink()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = {
                "success": True,
                "video_url": f"/videos/{video_name}",
                "duration": duration,
                "has_audio": has_audio,
                "image_count": len(images)
            }
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    print(f"🎬 Promo API (升级版) on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
