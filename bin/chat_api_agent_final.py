#!/usr/bin/env python3
"""Chat API - 完整版：TenantAgent 直接处理所有请求"""

import json
import sys
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# 添加路径
sys.path.insert(0, '/mnt/d/clawsjoy/agents')
from tenant_agent import TenantAgent

PORT = 18109

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/agent':
            self.send_error(404)
            return
        
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        user_input = data.get('text', data.get('message', ''))
        tenant_id = data.get('tenant_id', 'tenant_1')
        
        # 获取租户专属 Agent
        agent = TenantAgent(tenant_id)
        
        # ========== 直接调用 Agent 的智能处理 ==========
        result = agent.process_user_request(user_input)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🤖 Chat API (TenantAgent 模式) 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
