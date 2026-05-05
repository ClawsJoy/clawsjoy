#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import uuid
import os

VIDEO_DIR = "/home/flybo/clawsjoy/web/videos"
os.makedirs(VIDEO_DIR, exist_ok=True)


class PromoHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/promo/make":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            city = data.get("city", "香港")
            style = data.get("style", "科技")

            video_file = f"{VIDEO_DIR}/{city}_{style}_{uuid.uuid4().hex[:8]}.mp4"

            # 正确的 ffmpeg 命令
            cmd = [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "color=c=blue:s=1920x1080:d=3",
                "-vf",
                f"drawtext=text='{city} {style}':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v",
                "libx264",
                "-y",
                video_file,
            ]

            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0 and os.path.exists(video_file):
                self.send_json(
                    {
                        "success": True,
                        "video_url": f"/videos/{os.path.basename(video_file)}",
                    }
                )
            else:
                self.send_json(
                    {"success": False, "error": result.stderr.decode()[:200]}
                )
        else:
            self.send_error(404)

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


if __name__ == "__main__":
    port = 8086
    print(f"Promo API on port {port}")
    HTTPServer(("0.0.0.0", port), PromoHandler).serve_forever()
