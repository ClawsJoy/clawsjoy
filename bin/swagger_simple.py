#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>ClawsJoy API 文档</title></head>
<body style="background:#0f0f1a;color:#fff;font-family:monospace;padding:20px">
<h1>🦞 ClawsJoy API 文档</h1>
<h2>🔗 核心 API 端点</h2>
<ul>
<li><a href="http://redis:8088/api/tenants">GET /api/tenants</a> - 租户列表</li>
<li><a href="http://redis:8092/api/auth/health">GET /api/auth/health</a> - 健康检查</li>
<li><a href="http://redis:8084/api/task/promo">POST /api/task/promo</a> - 制作宣传片</li>
<li><a href="http://redis:8085/api/coffee/shops">GET /api/coffee/shops</a> - 咖啡店列表</li>
</ul>
<h2>📊 管理界面</h2>
<ul>
<li><a href="/workflow/">📈 Workflow 监控</a></li>
<li><a href="/joymate/?tenant=1">🦞 Joy Mate (租户1)</a></li>
<li><a href="/tenant/">🔐 租户登录</a></li>
</ul>
<h2>📦 快速测试</h2>
<pre>
curl http://redis:8088/api/tenants
curl -X POST http://redis:8092/api/auth/login -d '{"username":"admin","password":"admin123"}' -H "Content-Type: application/json"
curl -X POST http://redis:8084/api/task/promo -d '{"city":"香港"}' -H "Content-Type: application/json"
</pre>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))


if __name__ == "__main__":
    port = 8094
    print(f"API Docs: http://redis:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
