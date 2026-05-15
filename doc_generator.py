#!/usr/bin/env python3
"""文档生成服务"""
from flask import Flask, jsonify, request
from pathlib import Path

app = Flask(__name__)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "doc_generator"})

@app.route('/md', methods=['POST'])
def create_md():
    data = request.json
    title = data.get('title', '未命名')
    content = data.get('content', '')
    filename = f"generated_{title.replace(' ', '_')}.md"
    file_path = UPLOAD_DIR / filename
    file_path.write_text(f"# {title}\n\n{content}", encoding='utf-8')
    return jsonify({'success': True, 'filename': filename})

if __name__ == '__main__':
    print("📝 文档生成服务启动: http://localhost:5008")
    app.run(host='0.0.0.0', port=5008, debug=False)
