#!/usr/bin/env python3
"""完整版 Promo API - 多图轮播 + 配音解说"""

import os
import json
import time
import uuid
import requests
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

UNSPLASH_KEY = "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs"
PORT = 8108
IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images")
VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

def fetch_images(keyword, count=12):
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
    """生成配音"""
    try:
        safe_script = script.replace('"', '\\"')
        cmd = f'edge-tts --text "{safe_script}" --write-media {output_path} --voice zh-CN-XiaoxiaoNeural'
        subprocess.run(cmd, shell=True, timeout=120)
        return output_path.exists() and output_path.stat().st_size > 1000
    except Exception as e:
        print(f"TTS错误: {e}")
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
        
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            topic = data.get('topic', '香港')
            script = data.get('script', '')
            
            print(f"🎬 生成视频: {topic}")
            print(f"📝 脚本长度: {len(script)}")
            
            # 1. 采集多张图片
            images = fetch_images("Hong Kong", 12)
            if not images:
                self.send_json({"success": False, "error": "No images"})
                return
            
            # 2. 生成配音
            audio_file = Path(f"/tmp/tts_{int(time.time())}.mp3")
            has_audio = generate_tts(script, audio_file) if script else False
            
            # 3. 获取音频时长
            duration = 15
            if has_audio:
                result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_file)], capture_output=True, text=True)
                try:
                    duration = float(result.stdout.strip())
                except:
                    duration = 15
            
            # 4. 创建 concat 文件（多图轮播）
            video_name = f"hk_{int(time.time())}.mp4"
            video_path = VIDEO_DIR / video_name
            concat_file = Path("/tmp/concat.txt")
            
            per_image = duration / len(images)
            with open(concat_file, 'w') as f:
                for img in images:
                    f.write(f"file '{img}'\n")
                    f.write(f"duration {per_image}\n")
            
            # 5. 合成视频（图片+配音）
            if has_audio:
                cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -i {audio_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -c:a aac -shortest -pix_fmt yuv420p -y "{video_path}"'
            else:
                cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -pix_fmt yuv420p -y "{video_path}"'
            
            subprocess.run(cmd, shell=True)
            
            # 清理
            os.remove(concat_file)
            if audio_file.exists():
                os.remove(audio_file)
            
            if video_path.exists() and video_path.stat().st_size > 0:
                self.send_json({"success": True, "video_url": f"/videos/{video_name}", "image_count": len(images), "duration": duration, "has_audio": has_audio})
            else:
                self.send_json({"success": False, "error": "视频生成失败"})
        except Exception as e:
            print(f"错误: {e}")
            self.send_json({"success": False, "error": str(e)})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"🎬 完整版 Promo API on port {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
