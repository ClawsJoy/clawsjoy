#!/usr/bin/env python3
"""ClawsJoy 稳定版 - 任务调度器"""

import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 添加路径
sys.path.insert(0, '/mnt/d/clawsjoy/stable')
from config.settings import *

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskHandler(BaseHTTPRequestHandler):
    
    def send_json(self, data, status=200):
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        except Exception as e:
            logger.error(f"发送响应失败: {e}")
    
    def send_error(self, code, message=None):
        self.send_json({'success': False, 'error': message or 'Unknown error'}, code)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            
            if parsed.path == '/api/list_engines':
                self._handle_list_engines()
            elif parsed.path.startswith('/api/library/list'):
                self._handle_library_list(parsed)
            elif parsed.path.startswith('/api/file/'):
                self._handle_serve_file(parsed)
            else:
                self.send_error(404, f'Not found: {parsed.path}')
        except Exception as e:
            logger.error(f"GET 处理失败: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            
            if parsed.path == '/api/chat':
                self._handle_chat()
            elif parsed.path == '/api/library/upload':
                self._handle_upload()
            else:
                self.send_error(404, f'Not found: {parsed.path}')
        except Exception as e:
            logger.error(f"POST 处理失败: {e}")
            self.send_error(500, str(e))
    
    def _handle_list_engines(self):
        self.send_json({
            'success': True,
            'engines': ['openclaw', 'claude_code', 'self'],
            'current': 'self'
        })
    
    def _handle_library_list(self, parsed):
        tenant_id = parse_qs(parsed.query).get('tenant_id', [DEFAULT_TENANT])[0]
        lib_dir = TENANTS_ROOT / f"tenant_{tenant_id}" / "library" / "images"
        
        if not lib_dir.exists():
            self.send_json({'success': True, 'files': []})
            return
        
        files = []
        for i, f in enumerate(lib_dir.iterdir()):
            if f.is_file():
                files.append({
                    'id': i,
                    'name': f.name,
                    'path': f"/api/file/{f.name}",
                    'size': f.stat().st_size
                })
        
        self.send_json({'success': True, 'files': files})
    
    def _handle_serve_file(self, parsed):
        filename = parsed.path.split('/')[-1]
        
        # 在所有租户中查找文件
        found = None
        for tenant_dir in TENANTS_ROOT.iterdir():
            if tenant_dir.is_dir():
                img_dir = tenant_dir / "library" / "images"
                if img_dir.exists():
                    for f in img_dir.iterdir():
                        if f.name == filename:
                            found = f
                            break
                if found:
                    break
        
        if found and found.exists():
            self._send_file(found)
        else:
            self.send_error(404, f"File not found: {filename}")
    
    def _send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                import mimetypes
                mime = mimetypes.guess_type(str(filepath))[0] or 'application/octet-stream'
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            logger.error(f"文件发送失败: {e}")
            self.send_error(500, str(e))
    
    def _handle_chat(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        message = data.get('message', '')
        tenant_id = data.get('tenant_id', DEFAULT_TENANT)
        
        logger.info(f"租户 {tenant_id} 聊天: {message[:50]}")
        
        # 调用 Ollama
        try:
            import requests
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={'model': OLLAMA_MODEL, 'prompt': message, 'stream': False},
                timeout=OLLAMA_TIMEOUT
            )
            if resp.status_code == 200:
                reply = resp.json().get('response', '收到')
            else:
                reply = f'AI 服务异常: {resp.status_code}'
        except requests.exceptions.Timeout:
            reply = 'AI 响应超时，请稍后再试'
        except Exception as e:
            logger.error(f"Ollama 调用失败: {e}")
            reply = 'AI 服务暂时不可用'
        
        self.send_json({'success': True, 'message': reply})
    
    def _handle_upload(self):
        # TODO: 实现文件上传
        self.send_json({'success': False, 'error': '上传功能开发中'})
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    """启动服务"""
    # 确保必要目录存在
    LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"启动 ClawsJoy 任务调度器 v2.0")
    logger.info(f"端口: {PORT_TASK_API}")
    logger.info(f"日志: {LOG_FILE}")
    
    server = HTTPServer(('0.0.0.0', PORT_TASK_API), TaskHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务已停止")
        server.shutdown()

if __name__ == '__main__':
    main()
