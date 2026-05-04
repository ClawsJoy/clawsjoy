#!/usr/bin/env python3
import os
import tempfile
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import whisper

print("🔄 加载 Whisper 模型...")
model = whisper.load_model("tiny")
print("✅ 模型加载完成")

class WhisperHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/stt':
            try:
                length = int(self.headers.get('Content-Length', 0))
                audio_data = self.rfile.read(length)
                
                # 保存为临时文件
                with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                    f.write(audio_data)
                    temp_path = f.name
                
                # 转文字
                result = model.transcribe(temp_path)
                text = result['text'].strip()
                
                os.unlink(temp_path)
                print(f"识别: {text}")
                
                self.send_json({'success': True, 'text': text})
            except Exception as e:
                print(f"错误: {e}")
                self.send_json({'success': False, 'error': str(e)})
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    port = 8096
    print(f"🎤 Whisper STT: http://redis:{port}")
    HTTPServer(('0.0.0.0', port), WhisperHandler).serve_forever()
