#!/usr/bin/env python3
"""Workflow API - 供前端调用"""

import json
import pickle
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

STATE_DIR = Path("/home/flybo/clawsjoy/data/workflow_states")
STATE_DIR.mkdir(parents=True, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/workflow/list':
            workflows = []
            for f in STATE_DIR.glob("*.pkl"):
                try:
                    with open(f, 'rb') as fp:
                        state = pickle.load(fp)
                    workflows.append({
                        "id": state.get("workflow_id", f.stem),
                        "status": state.get("status", "unknown"),
                        "progress": f"{state.get('current_step_index', 0)}/{len(state.get('steps', []))}",
                        "updated_at": state.get("updated_at", "")
                    })
                except:
                    pass
            self.send_json({"workflows": workflows})
        
        elif parsed.path == '/api/workflow/detail':
            params = parse_qs(parsed.query)
            workflow_id = params.get('workflow_id', [''])[0]
            for f in STATE_DIR.glob(f"*{workflow_id}*.pkl"):
                try:
                    with open(f, 'rb') as fp:
                        state = pickle.load(fp)
                    steps = []
                    for s in state.get("steps", []):
                        steps.append({
                            "name": s.get("name"),
                            "skill": s.get("skill"),
                            "status": s.get("status")
                        })
                    self.send_json({
                        "workflow_id": state.get("workflow_id"),
                        "status": state.get("status"),
                        "steps": steps,
                        "updated_at": state.get("updated_at")
                    })
                    return
                except:
                    pass
            self.send_json({"error": "not found"}, 404)
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
    
    def log_message(self, *a): pass

if __name__ == '__main__':
    port = 8093
    print(f"Workflow API: http://redis:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
