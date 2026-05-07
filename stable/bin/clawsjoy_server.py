#!/usr/bin/env python3
"""ClawsJoy 统一服务 - 稳定版"""

import json
import logging
import sys
import os
import sqlite3
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 添加配置路径
sys.path.insert(0, '/mnt/d/clawsjoy/stable')
from config.settings import *

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ClawsJoy")

class ClawsJoyHandler(BaseHTTPRequestHandler):
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    # ========== GET 请求处理 ==========
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/health':
            self._handle_health()
        elif parsed.path == '/api/list_engines':
            self._handle_list_engines()
        elif parsed.path.startswith('/api/tenants'):
            self._handle_tenants()
        elif parsed.path.startswith('/api/library/list'):
            self._handle_library_list(parsed)
        elif parsed.path.startswith('/api/file/'):
            self._handle_serve_file(parsed)
        else:
            self.send_error(404, f'未找到: {parsed.path}')
    
    # ========== POST 请求处理 ==========
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/chat':
            self._handle_chat()
        elif parsed.path == '/api/library/upload':
            self._handle_upload()
        elif parsed.path == '/api/auth/login':
            self._handle_login()
        else:
            self.send_error(404, f'未找到: {parsed.path}')
    
    # ========== 业务方法 ==========
    def _handle_health(self):
        self.send_json({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'api': 'running',
                'ollama': self._check_ollama()
            }
        })
    
    def _check_ollama(self):
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            return 'running' if resp.status_code == 200 else 'error'
        except:
            return 'not available'
    
    def _handle_list_engines(self):
        self.send_json({
            'success': True,
            'engines': ['openclaw', 'claude_code', 'self'],
            'current': 'self'
        })
    
    def _handle_tenants(self):
        tenants = [
            {'id': '1', 'name': '租户 1'},
            {'id': '2', 'name': '租户 2'},
            {'id': '3', 'name': '租户 3'}
        ]
        self.send_json({'success': True, 'tenants': tenants})
    
    def _handle_library_list(self, parsed):
        tenant_id = parse_qs(parsed.query).get('tenant_id', ['1'])[0]
        lib_dir = TENANTS_DIR / f"tenant_{tenant_id}" / "library" / "images"
        
        if not lib_dir.exists():
            self.send_json({'success': True, 'files': []})
            return
        
        files = []
        for f in lib_dir.iterdir():
            if f.is_file():
                files.append({
                    'name': f.name,
                    'size': f.stat().st_size,
                    'url': f"/api/file/{f.name}"
                })
        self.send_json({'success': True, 'files': files})
    
    def _handle_serve_file(self, parsed):
        filename = parsed.path.split('/')[-1]
        found = None
        
        for tenant_dir in TENANTS_DIR.iterdir():
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
            self.send_error(404, f'文件不存在: {filename}')
    
    def _send_file(self, filepath):
        import mimetypes
        try:
            with open(filepath, 'rb') as f:
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
        tenant_id = data.get('tenant_id', '1')
        
        logger.info(f"租户 {tenant_id}: {message[:50]}")
        
        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={'model': OLLAMA_MODEL, 'prompt': message, 'stream': False},
                timeout=30
            )
            if resp.status_code == 200:
                reply = resp.json().get('response', '收到')
            else:
                reply = f'AI 服务异常: {resp.status_code}'
        except requests.exceptions.Timeout:
            reply = 'AI 响应超时，请稍后再试'
        except Exception as e:
            logger.error(f"Ollama 错误: {e}")
            reply = 'AI 服务暂时不可用'
        
        self.send_json({'success': True, 'message': reply})
    
    def _handle_upload(self):
        # TODO: 实现文件上传
        self.send_json({'success': False, 'message': '上传功能开发中'})
    
    def _handle_login(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username == 'admin' and password == 'admin123':
            self.send_json({'success': True, 'token': 'mock-token', 'user': {'name': 'admin'}})
        else:
            self.send_json({'success': False, 'error': '用户名或密码错误'}, 401)
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def main():
    logger.info("=" * 50)
    logger.info("ClawsJoy 统一服务启动")
    logger.info(f"端口: {PORT_TASK}")
    logger.info(f"日志: {LOG_FILE}")
    logger.info("=" * 50)
    
    server = HTTPServer(('0.0.0.0', PORT_TASK), ClawsJoyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务已停止")
        server.shutdown()

if __name__ == '__main__':
    main()
