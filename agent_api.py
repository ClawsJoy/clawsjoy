#!/usr/bin/env python3
"""Agent API - 统一调用接口"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from lib.unified_config import config

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "agent_api"})

@app.route('/agents', methods=['GET'])
def list_agents():
    return jsonify({"agents": [], "message": "Agent API 运行中"})

if __name__ == '__main__':
    port = config.get_port('agent_api')
    print(f"🤖 Agent API 启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
