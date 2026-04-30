#!/usr/bin/env python3
import subprocess, json, os, time
from http.server import HTTPServer, BaseHTTPRequestHandler

def make_promo(city, style):
    keyword = f"{city}{style}"
    subprocess.run(f"/root/clawsjoy/bin/spider_unsplash '{city} {style}' 3", shell=True, timeout=30)
    time.sleep(2)
    output = f"/root/.openclaw/web/videos/{city}_{style}_{int(time.time())}.mp4"
    subprocess.run(f"/root/clawsjoy/bin/make_video '{keyword}' '/root/.openclaw/web/images/{city}/' '{output}' '{keyword}'", shell=True, timeout=120)
    return output if os.path.exists(output) and os.path.getsize(output)>10000 else None

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        video = make_promo(body.get('city','香港'), body.get('style','科技'))
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": video is not None, "video_url": f"/videos/{os.path.basename(video)}" if video else ""}).encode())
    def log_message(self, *a): pass

print("API running on 8087")
HTTPServer(("0.0.0.0", 8087), Handler).serve_forever()
