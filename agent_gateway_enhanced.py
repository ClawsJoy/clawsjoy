#!/usr/bin/env python3
"""ClawsJoy Gateway - Simplified Version"""

import json
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========== 健康检查 ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'clawsjoy-gateway', 'version': '4.0.0'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'service': 'ClawsJoy Gateway', 'version': '4.0.0'})

# ========== 技能列表 ==========
@app.route('/api/skills/list', methods=['GET'])
def list_skills():
    """获取技能列表"""
    try:
        from core.lib.skill_loader_v3 import skill_loader
        skills = skill_loader.list_skills()
        return jsonify({'success': True, 'total': len(skills), 'skills': skills})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 智能体列表 ==========
@app.route('/api/agents/list', methods=['GET'])
def list_agents():
    """获取智能体列表"""
    agents = [
        {"name": "chat_agent", "status": "active", "version": "2.0.0"},
        {"name": "code_agent", "status": "active", "version": "1.0.0"},
        {"name": "analysis_agent", "status": "active", "version": "1.0.0"},
        {"name": "decision_agent", "status": "active", "version": "1.0.0"}
    ]
    return jsonify({'success': True, 'total': len(agents), 'agents': agents})

# ========== 增强对话 ==========
@app.route('/api/v5/enhanced/chat', methods=['POST'])
def enhanced_chat():
    """增强对话"""
    data = request.json or {}
    message = data.get('message', '')
    user_id = data.get('user_id', 'guest')
    
    # 简单响应
    response = f"收到您的消息: {message}"
    return jsonify({
        'success': True,
        'response': response,
        'agent': 'chat_agent',
        'enhanced': True,
        'user_id': user_id
    })

# ========== 记忆存储 ==========
@app.route('/api/v5/memory/remember', methods=['POST'])
def memory_remember():
    data = request.json or {}
    return jsonify({'success': True, 'message': '记忆已存储'})

# ========== 记忆检索 ==========
@app.route('/api/v5/memory/recall', methods=['POST'])
def memory_recall():
    data = request.json or {}
    return jsonify({'success': True, 'results': []})

if __name__ == '__main__':
    port = 5002
    print(f"🚀 ClawsJoy Gateway 启动在端口 {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
