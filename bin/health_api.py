#!/usr/bin/env python3
"""健康检查 API - 返回系统状态"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from metrics_collector import collect_metrics, check_alerts

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            metrics = collect_metrics()
            alerts = check_alerts(metrics)
            
            # 计算健康分
            up = sum(1 for s in metrics["services"].values() if s.get("status") == "up")
            total = len(metrics["services"])
            health_score = int(up / total * 100) if total > 0 else 0
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = {
                "status": "healthy" if health_score >= 80 else "degraded",
                "health_score": health_score,
                "services": metrics["services"],
                "resources": metrics["resources"],
                "alerts": alerts
            }
            self.wfile.write(json.dumps(result, indent=2).encode())
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

if __name__ == '__main__':
    port = 18110
    print(f"🩺 健康检查 API 启动: http://localhost:{port}/health")
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()
