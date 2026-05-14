#!/usr/bin/env python3
"""多智能体服务"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

app = Flask(__name__)
CORS(app)

# 加载编排器
from agents.multi.orchestrator import MultiAgentOrchestrator
orchestrator = MultiAgentOrchestrator()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'multi-agent'})

@app.route('/agents', methods=['GET'])
def list_agents():
    return jsonify({'agents': orchestrator.list_agents()})

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    goal = data.get('goal', '')
    result = orchestrator.execute(goal)
    return jsonify(result)

if __name__ == '__main__':
    print("🤝 多智能体服务启动: http://localhost:5005")
    app.run(host='0.0.0.0', port=5005, debug=False)
