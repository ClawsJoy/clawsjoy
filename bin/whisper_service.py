#!/usr/bin/env python3
import os
import tempfile
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import whisper
from datetime import datetime

print("🔄 加载 Whisper 模型...")
model = whisper.load_model("base")
print("✅ 模型就绪")

class Handler(BaseHTTPRequestHandler):
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
                
                print(f"收到音频: {len(audio_data)} bytes")
                
                # 保存原始音频
                webm_file = f"/tmp/audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
                with open(webm_file, 'wb') as f:
                    f.write(audio_data)
                
                # 转换为 WAV 格式
                wav_file = webm_file.replace('.webm', '.wav')
                convert_cmd = ['ffmpeg', '-i', webm_file, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav_file, '-y']
                result = subprocess.run(convert_cmd, capture_output=True)
                
                if result.returncode != 0:
                    print(f"转换失败: {result.stderr.decode()}")
                    self.send_json({'success': False, 'error': '音频转换失败'})
                    os.unlink(webm_file)
                    return
                
                # Whisper 识别
                result = model.transcribe(wav_file)
                text = result['text'].strip()
                print(f"识别结果: '{text}'")
                
                # 清理临时文件
                os.unlink(webm_file)
                os.unlink(wav_file)
                
                self.send_json({'success': True, 'text': text})
                
            except Exception as e:
                print(f"错误: {e}")
                self.send_json({'success': False, 'error': str(e)})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    port = 8096
    print(f"🎤 Whisper STT 服务: http://redis:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
