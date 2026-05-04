#!/usr/bin/env python3
import json, threading, time, subprocess, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/web/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def make_promo(city, style):
    """真正生成视频"""
    try:
        # 采集图片
        keyword = f"{city}{style}"
        subprocess.run(f"/root/clawsjoy/bin/spider_unsplash '{city} {style}' 3", shell=True, timeout=30)
        time.sleep(2)
        
        # 生成视频
        output_file = OUTPUT_DIR / f"{city}_{style}_{int(time.time())}.mp4"
        script = f"{city}{style}宣传片"
        
        cmd = f"/root/clawsjoy/bin/make_video '{script}' '/root/.openclaw/web/images/{city}/' '{output_file}' '{keyword}'"
        subprocess.run(cmd, shell=True, timeout=120)
        
        if output_file.exists() and output_file.stat().st_size > 10000:
            print(f"✅ 视频已生成: {output_file.name}")
        else:
            print("⚠️ 生成占位视频")
            subprocess.run(f"ffmpeg -f lavfi -i color=c=#667eea:s=1280x720:d=5 -vf 'drawtext=text={city}{style}宣传片:fontcolor=white:fontsize=48' -y {output_file}", shell=True)
    except Exception as e:
        print(f"❌ 错误: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/promo/make':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            city = body.get('city', '香港')
            style = body.get('style', '科技')
            
            # 异步生成视频
            threading.Thread(target=make_promo, args=(city, style)).start()
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            # 返回视频URL（使用最新视频）
            videos = sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
            video_url = f"/videos/{videos[0].name}" if videos else ""
            self.wfile.write(json.dumps({
                "success": True, 
                "message": f"🎬 开始制作{city}{style}宣传片",
                "video_url": video_url
            }).encode())
    
    def log_message(self, format, *args): pass

print("🎬 宣传片 API (视频版): http://redis:8086")
HTTPServer(("0.0.0.0", 8086), Handler).serve_forever()
