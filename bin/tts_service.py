#!/usr/bin/env python3
"""TTS 服务 - 支持多种音色"""

import json
import edge_tts
import asyncio
import tempfile
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class TTSHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/tts':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            text = data.get('text', '')
            voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
            
            if not text:
                self.send_json({'error': 'text required'}, 400)
                return
            
            async def generate():
                tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                tmp.close()
                await edge_tts.Communicate(text, voice).save(tmp.name)
                return tmp.name
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_file = loop.run_until_complete(generate())
                
                with open(audio_file, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f.read())
                os.unlink(audio_file)
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    port = 9000
    print(f"🎤 TTS 服务: http://localhost:{port}")
    HTTPServer(('0.0.0.0', port), TTSHandler).serve_forever()
