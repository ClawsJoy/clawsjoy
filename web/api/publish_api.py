#!/usr/bin/env python3
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/api/publish', methods=['POST'])
def publish():
    data = request.json
    pub_type = data.get('type')
    content = data.get('content')
    
    if pub_type == 'youtube':
        result = subprocess.run(f'openclaw agent --to messenger --message "发布YouTube: {content}"', shell=True, capture_output=True)
    elif pub_type == 'xiaohongshu':
        result = subprocess.run(f'openclaw agent --to messenger --message "发布小红书: {content}"', shell=True, capture_output=True)
    else:
        return jsonify({'error': 'unknown type'}), 400
    
    return jsonify({'status': 'success', 'output': result.stdout})

if __name__ == '__main__':
    app.run(port=8083)
