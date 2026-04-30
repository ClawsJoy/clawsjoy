#!/usr/bin/env python3
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import sys

DATA_FILE = os.path.expanduser("~/.openclaw/web/review/data/queue.json")

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/decide':
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            
            item_id = body.get('id')
            decision = body.get('decision')
            reviewer = body.get('reviewer', 'John')
            
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            success = False
            for i, item in enumerate(data.get("pending_final", [])):
                if item.get("id") == item_id:
                    item["final_decision"] = decision
                    item["final_reviewer"] = reviewer
                    item["final_at"] = datetime.now().isoformat()
                    item["status"] = "completed"
                    data.setdefault("completed", []).insert(0, item)
                    del data["pending_final"][i]
                    success = True
                    break
            
            if success:
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": f"已{decision}"}).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "未找到该项"}).encode())

if __name__ == '__main__':
    from http.server import HTTPServer
    port = 8083
    print(f"API 服务启动在端口 {port}")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
