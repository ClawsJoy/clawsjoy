import json
import asyncio
import edge_tts
from http.server import HTTPServer, BaseHTTPRequestHandler


class TTSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/tts":
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length))
                text = data.get("text", "")
                voice = data.get("voice", "zh-CN-XiaoxiaoNeural")

                # 生成音频
                async def generate():
                    communicate = edge_tts.Communicate(text, voice)
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]
                    return audio_data

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_data = loop.run_until_complete(generate())
                loop.close()

                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", len(audio_data))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(audio_data)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    port = 9000
    print(f"TTS Server (edge-tts) running on port {port}")
    HTTPServer(("0.0.0.0", port), TTSHandler).serve_forever()
