#!/usr/bin/env python3
"""TTS 服务 - 文字转语音"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import edge_tts
import asyncio
import tempfile
import os


class TTSHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/tts":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            text = data.get("text", "")

            async def gen():
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp.close()
                await edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural").save(tmp.name)
                return tmp.name

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_file = loop.run_until_complete(gen())

            with open(audio_file, "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(f.read())
            os.unlink(audio_file)
        else:
            self.send_error(404)


if __name__ == "__main__":
    port = 9000
    print(f"✅ TTS 服务启动: http://redis:{port}")
    HTTPServer(("0.0.0.0", port), TTSHandler).serve_forever()
