#!/usr/bin/env python3
"""健康检查汇总服务"""

import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

SERVICES = {
    "auth": "http://localhost:8092/api/auth/health",
    "tenant": "http://localhost:8088/api/tenants",
    "billing": "http://localhost:8090/api/billing/balance?tenant_id=1",
}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            status = {}
            for name, url in SERVICES.items():
                try:
                    with urllib.request.urlopen(url, timeout=3) as resp:
                        status[name] = {"status": "up", "code": resp.getcode()}
                except Exception as e:
                    status[name] = {"status": "down", "error": str(e)}
            
            all_up = all(s["status"] == "up" for s in status.values())
            http_code = 200 if all_up else 503
            
            self.send_response(http_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "service": "clawsjoy",
                "status": "healthy" if all_up else "degraded",
                "checks": status
            }).encode())
        else:
            self.send_error(404)
    
    def log_message(self, *args): pass

if __name__ == '__main__':
    port = 8095
    print(f"📊 健康检查: http://localhost:{port}/health")
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
