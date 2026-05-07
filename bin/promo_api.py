#!/usr/bin/env python3
"""Promo API - 完整版"""

import json
import time
import uuid
import requests
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8108
UNSPLASH_KEY = "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs"

BASE_DIR = Path("/mnt/d/clawsjoy")
VIDEO_DIR = BASE_DIR / "web/videos"
IMAGE_DIR = BASE_DIR / "web/images"
AUDIO_DIR = BASE_DIR / "web/audio"

for d in [VIDEO_DIR, IMAGE_DIR, AUDIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def fetch_images(keyword, count=10):
    # 本地图片降级
    if not images:
        local_dir = Path("/mnt/d/clawsjoy/web/images/local")
        if local_dir.exists():
            local_images = list(local_dir.glob("*.jpg"))
            images = [str(img) for img in local_images[:count]]
            print(f"使用本地图片: {len(images)}张")
    images = []
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": keyword, "per_page": count, "orientation": "landscape"}
        headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            for photo in resp.json().get('results', [])[:count]:
                img_url = photo['urls']['regular']
                img_data = requests.get(img_url, timeout=30).content
                img_path = IMAGE_DIR / f"{uuid.uuid4().hex}.jpg"
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                images.append(str(img_path))
        print(f"✅ 采集 {len(images)} 张图片")
    except Exception as e:
        print(f"❌ 采集失败: {e}")
    return images

def generate_tts(text, output_path):
    try:
        safe = text.replace('"', '\\"')
        cmd = f'edge-tts --text "{safe}" --write-media {output_path} --voice zh-CN-XiaoxiaoNeural'
        subprocess.run(cmd, shell=True, timeout=120)
        return output_path.exists() and output_path.stat().st_size > 1000
    except Exception as e:
        print(f"❌ TTS: {e}")
        return False

def get_bgm():
    files = list(AUDIO_DIR.glob("*.mp3"))
    return str(files[0]) if files else None

def compose_video(images, audio_path, output_path, duration, topic):
    if not images:
        return False
    per_img = duration / len(images)
    concat_file = Path(f"/tmp/concat_{int(time.time())}.txt")
    with open(concat_file, 'w') as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write(f"duration {per_img}\n")
    
    font = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    subtitle = f"{topic} 科技宣传片"
    
    if audio_path and Path(audio_path).exists():
        bgm = get_bgm()
        if bgm:
            mixed = Path(f"/tmp/mixed_{int(time.time())}.mp3")
            mix = f'ffmpeg -i {audio_path} -i {bgm} -filter_complex "[0:a]volume=1[a1];[1:a]volume=0.15[a2];[a1][a2]amix=inputs=2" -c:a libmp3lame -q:a 2 -y {mixed}'
            subprocess.run(mix, shell=True)
            final_audio = mixed
        else:
            final_audio = audio_path
        cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -i {final_audio} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile={font}:text=\'{subtitle}\':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100" -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 -shortest -pix_fmt yuv420p -crf 18 -preset medium -y "{output_path}"'
    else:
        cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile={font}:text=\'{subtitle}\':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -y "{output_path}"'
    
    subprocess.run(cmd, shell=True)
    success = output_path.exists() and output_path.stat().st_size > 0
    concat_file.unlink()
    for img in images:
        Path(img).unlink()
    if 'mixed' in locals() and mixed.exists():
        mixed.unlink()
    return success

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
        topic = data.get('topic', data.get('city', '香港'))
        duration = data.get('duration', 30)
        script = data.get('script', f"{topic}科技宣传片：创新、活力、未来。")
        
        print(f"🎬 制作 {topic}，{duration}秒")
        images = fetch_images(topic, count=min(20, max(5, duration // 3)))
        audio_file = Path(f"/tmp/tts_{int(time.time())}.mp3")
        has_audio = generate_tts(script, audio_file)
        video_name = f"promo_{topic}_{int(time.time())}.mp4"
        video_path = VIDEO_DIR / video_name
        success = compose_video(images, audio_file if has_audio else None, video_path, duration, topic)
        if audio_file.exists():
            audio_file.unlink()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        result = {"success": success, "video_url": f"/videos/{video_name}" if success else None, "duration": duration, "has_audio": has_audio, "image_count": len(images)}
        self.wfile.write(json.dumps(result).encode())

if __name__ == '__main__':
    print(f"🎬 完整版 Promo API 端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

# 增加连接池配置，解决连接问题
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置重试策略
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 替换所有 requests 调用为 session
