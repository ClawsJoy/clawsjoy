#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, uuid, mimetypes
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                self.send_response(200)
                mime = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
                self.send_header('Content-Type', mime)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(404, str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/list_engines':
            self.send_json({'engines': ['openclaw', 'claude_code', 'self']})
        elif self.path.startswith('/api/library/list'):
            tenant_id = parse_qs(urlparse(self.path).query).get('tenant_id', ['1'])[0]
            lib_dir = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library/images")
            lib_dir.mkdir(parents=True, exist_ok=True)
            files = []
            for i, f in enumerate(lib_dir.iterdir()):
                if f.is_file():
                    files.append({'id': i, 'name': f.name, 'path': f"/api/file/{f.name}", 'size': f.stat().st_size})
            self.send_json({'success': True, 'files': files})
        elif self.path.startswith('/api/file/'):
            filename = self.path.split('/')[-1]
            # 在所有租户目录中查找文件
            tenants_dir = Path("/home/flybo/clawsjoy/tenants")
            found = None
            for tenant_dir in tenants_dir.iterdir():
                if tenant_dir.is_dir():
                    img_dir = tenant_dir / "library/images"
                    if img_dir.exists():
                        for f in img_dir.iterdir():
                            if f.name == filename:
                                found = f
                                break
                    if found:
                        break
            if found and found.exists():
                self.send_file(found)
            else:
                self.send_error(404)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/chat':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            self.send_json({'message': f'收到: {data.get("message", "")}'})
        elif self.path == '/api/library/upload':
            self.send_json({'success': True})
        else:
            self.send_error(404)

if __name__ == '__main__':
    port = 8084
    print(f"API Server on http://localhost:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
