#!/usr/bin/env python3
"""Chat API - 基于关键词编排"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, '/mnt/d/clawsjoy/agents')
from orchestrator import OrchestratorAgent

PORT = 18109

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        user_input = data.get('text', data.get('message', ''))
        tenant_id = data.get('tenant_id', 'tenant_1')
        
        agent = OrchestratorAgent(tenant_id)
        result = agent.process(user_input)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

if __name__ == '__main__':
    print(f"🤖 关键词编排版 Chat API 启动在端口 {PORT}")
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
