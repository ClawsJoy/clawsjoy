#!/usr/bin/env python3
"""Agent API - 简化版"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "agent-api"})

@app.route('/agents', methods=['GET'])
def list_agents():
    return jsonify({
        "agents": ["code_agent", "video_agent", "youtube_agent", "orchestrator"],
        "total": 4
    })

if __name__ == '__main__':
    print("🤖 Agent API 启动: http://smart_config.HOST:5010")
    app.run(host='0.0.0.0', port=5010, debug=False)
