#!/usr/bin/env python3
"""简单的 Web Dashboard 服务器"""
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='web')

@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

if __name__ == '__main__':
    port = 5011
    print(f"📊 Web Dashboard 启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
