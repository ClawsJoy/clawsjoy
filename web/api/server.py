#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/agents':
            agents = []
            agents_dir = '/home/flybo/.openclaw/agents'
            if os.path.exists(agents_dir):
                for d in os.listdir(agents_dir):
                    if os.path.isdir(os.path.join(agents_dir, d)) and not d.startswith('.'):
                        agents.append({'name': d, 'status': 'idle'})
            self.send_json({'agents': agents, 'count': len(agents)})
        elif self.path == '/':
            self.send_file('/home/flybo/.openclaw/web/index.html')
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_file(self, path):
        with open(path, 'rb') as f:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f.read())

if __name__ == '__main__':
    port = 8080
    print(f"Web 服务启动: http://localhost:{port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
