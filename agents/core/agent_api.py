#!/usr/bin/env python3
"""Agent API - 租户通过HTTP与管家交互"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agents.tenant_agent import get_agent

class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/agent/chat':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get('tenant_id', 'tenant_1')
            message = data.get('message', '')
            
            agent = get_agent(tenant_id)
            result = agent.chat(message)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)

if __name__ == '__main__':
    port = 18103
    print(f"🤖 Agent API 端口: {port}")
    HTTPServer(('0.0.0.0', port), AgentHandler).serve_forever()
