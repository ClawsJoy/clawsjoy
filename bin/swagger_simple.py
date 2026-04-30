#!/usr/bin/env python3
"""简单 API 文档服务 - 无需额外依赖"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HTML = '''<!DOCTYPE html>
<html>
<head><title>ClawsJoy API 文档</title>
<style>
body{background:#0f0f1a;color:#fff;font-family:system-ui;padding:40px}
h1{color:#667eea}
.card{background:#1a1a2e;border-radius:16px;padding:20px;margin:20px 0}
.endpoint{background:#0f0f1a;padding:12px;border-radius:8px;margin:10px 0;font-family:monospace}
.get{background:#4caf50;padding:4px 12px;border-radius:6px;margin-right:10px}
.post{background:#ff9800;padding:4px 12px;border-radius:6px;margin-right:10px}
a{color:#667eea}
</style>
</head>
<body>
<h1>🦞 ClawsJoy API 文档</h1>

<div class="card">
<h2>🔗 核心 API 端点</h2>
<div class="endpoint"><span class="get">GET</span> /api/tenants - 租户列表</div>
<div class="endpoint"><span class="post">POST</span> /api/auth/login - 用户登录</div>
<div class="endpoint"><span class="get">GET</span> /api/billing/balance?tenant_id=1 - 余额查询</div>
<div class="endpoint"><span class="get">GET</span> /api/coffee/shops - 咖啡店列表</div>
<div class="endpoint"><span class="post">POST</span> /api/coffee/order - 下单</div>
</div>

<div class="card">
<h2>📊 管理界面</h2>
<div class="endpoint"><a href="/workflow/">📈 Workflow 监控</a></div>
<div class="endpoint"><a href="/joymate/?tenant=1">🦞 Joy Mate (租户1)</a></div>
<div class="endpoint"><a href="/tenant/">🔐 租户登录</a></div>
</div>

<div class="card">
<h2>📦 快速测试</h2>
<div class="endpoint">curl http://localhost:8088/api/tenants</div>
<div class="endpoint">curl -X POST http://localhost:8092/api/auth/login -d '{"username":"admin","password":"admin123"}' -H "Content-Type: application/json"</div>
</div>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/tenants':
            self.send_json({"success": True, "tenants": [{"id": "1", "name": "租户 1"}, {"id": "2", "name": "租户 2"}]})
        elif self.path == '/api/auth/health':
            self.send_json({"status": "ok"})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, *a): pass

if __name__ == '__main__':
    port = 8094
    print(f"📚 API 文档: http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
