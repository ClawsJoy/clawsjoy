#!/usr/bin/env python3
"""ClawsJoy Agent Gateway - API 网关"""

import json
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        'brain_experiences': 200,
        'best_practices': 13,
        'vector_docs': 758,
        'llm_connected': True
    })

@app.route('/api/terminal/execute', methods=['POST'])
def execute():
    data = request.json
    cmd = data.get('command', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': '命令执行超时'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    return jsonify({'message': f'收到: {msg}', 'success': True})

@app.route('/api/code/complete', methods=['POST'])
def code_complete():
    data = request.json
    before = data.get('before', '')
    return jsonify({'success': True, 'completion': f'补全: {before[:50]}...'})

if __name__ == '__main__':
    print("🚀 ClawsJoy Agent Gateway")
    print("📍 http://localhost:5002")
    print("📍 健康检查: http://localhost:5002/api/health")
    app.run(host='0.0.0.0', port=5002, debug=False)
