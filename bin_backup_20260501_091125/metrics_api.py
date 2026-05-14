#!/usr/bin/env python3
"""Prometheus 指标暴露服务"""

import time
import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            # 收集系统指标
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            
            metrics = f'''# HELP clawsjoy_cpu_percent CPU使用率
# TYPE clawsjoy_cpu_percent gauge
clawsjoy_cpu_percent {cpu_percent}
# HELP clawsjoy_memory_percent 内存使用率
# TYPE clawsjoy_memory_percent gauge
clawsjoy_memory_percent {mem.percent}
# HELP clawsjoy_memory_available 可用内存(MB)
# TYPE clawsjoy_memory_available gauge
clawsjoy_memory_available {mem.available // 1024 // 1024}
# HELP clawsjoy_up 服务是否运行
# TYPE clawsjoy_up gauge
clawsjoy_up 1
'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode())
        else:
            self.send_error(404)
    
    def log_message(self, *args): pass

if __name__ == '__main__':
    port = 8096
    print(f"📈 Prometheus 指标: http://localhost:{port}/metrics")
    HTTPServer(("0.0.0.0", port), MetricsHandler).serve_forever()
