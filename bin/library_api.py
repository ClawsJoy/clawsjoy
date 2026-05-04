#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import os

DB_PATH = "/mnt/d/clawsjoy/data/library.db"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/library/list":
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT filename, filesize FROM assets")
            rows = cursor.fetchall()
            conn.close()
            files = [{"filename": r[0], "size": r[1]} for r in rows]
            self.send_json(200, {"success": True, "files": files})
        else:
            self.send_json(404, {"error": "not found"})

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        print(f"[Library] {fmt % args}")

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8100), Handler).serve_forever()
