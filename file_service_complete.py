#!/usr/bin/env python3
"""文件服务"""
from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'file'})

@app.route('/list', methods=['GET'])
def list_files():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return jsonify({'files': files})

if __name__ == '__main__':
    print("📁 文件服务启动: http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=False)
