#!/usr/bin/env python3
"""ClawsJoy STT 服务 - 使用 Whisper"""
import os
import sys
import tempfile
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import whisper
from datetime import datetime

# 加载模型
print("🔄 加载 Whisper 模型...")
model = whisper.load_model("base")
print("✅ 模型就绪")

class STTHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/stt':
            try:
                content_type = self.headers.get('Content-Type', '')
                length = int(self.headers.get('Content-Length', 0))
                audio_data = self.rfile.read(length)
                
                print(f"收到请求, Content-Type: {content_type}, 大小: {len(audio_data)} bytes")
                
                # 保存原始音频
                ext = 'webm' if 'webm' in content_type else 'webm'
                tmp_input = tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False)
                tmp_input.write(audio_data)
                tmp_input.close()
                
                # 转换为 WAV
                tmp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                tmp_wav.close()
                
                cmd = [
                    'ffmpeg', '-i', tmp_input.name,
                    '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
                    '-y', tmp_wav.name
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"FFmpeg 错误: {result.stderr}")
                    self._send_error(f"音频转换失败: {result.stderr[:100]}")
                    os.unlink(tmp_input.name)
                    return
                
                # Whisper 识别
                print(f"正在识别: {tmp_wav.name}")
                transcribe_result = model.transcribe(tmp_wav.name)
                text = transcribe_result['text'].strip()
                
                print(f"识别结果: '{text}'")
                
                # 清理
                os.unlink(tmp_input.name)
                os.unlink(tmp_wav.name)
                
                self._send_response({'success': True, 'text': text})
                
            except Exception as e:
                print(f"异常: {e}")
                self._send_error(str(e))
        else:
            self.send_error(404)
    
    def _send_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, msg):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'error': msg}).encode())

if __name__ == '__main__':
    port = 8096
    print(f"🎤 ClawsJoy STT 服务: http://redis:{port}")
    HTTPServer(('0.0.0.0', port), STTHandler).serve_forever()
