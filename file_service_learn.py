#!/usr/bin/env python3
"""文件服务 - 带大脑学习"""

from flask import Flask, jsonify, request
from pathlib import Path
import urllib.parse
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

app = Flask(__name__)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/files', methods=['GET'])
def list_files():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    brain.record_experience(
        agent="file_service",
        action="列出文件",
        result={"success": True, "count": len(files)},
        context="list"
    )
    return jsonify({"files": files, "count": len(files)})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No filename'}), 400
    
    save_path = UPLOAD_DIR / file.filename
    file.save(save_path)
    
    brain.record_experience(
        agent="file_service",
        action=f"上传文件: {file.filename}",
        result={"success": True, "size": save_path.stat().st_size},
        context="upload"
    )
    return jsonify({'success': True, 'filename': file.filename})

@app.route('/read/<filename>', methods=['GET'])
def read_file(filename):
    filename = urllib.parse.unquote(filename)
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Not found'}), 404
    
    content = file_path.read_text(encoding='utf-8')
    
    brain.record_experience(
        agent="file_service",
        action=f"读取文件: {filename}",
        result={"success": True, "size": file_path.stat().st_size},
        context="read"
    )
    return jsonify({'filename': filename, 'content': content})

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    filename = urllib.parse.unquote(filename)
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Not found'}), 404
    
    file_path.unlink()
    
    brain.record_experience(
        agent="file_service",
        action=f"删除文件: {filename}",
        result={"success": True},
        context="delete"
    )
    return jsonify({'success': True, 'deleted': filename})

if __name__ == '__main__':
    print("📁 文件服务启动 (带学习) http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=False)
