#!/usr/bin/env python3
"""独立移动端服务"""

from flask import Flask, send_from_directory, request, jsonify
import os
import sys
sys.path.insert(0, '.')

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOBILE_DIR = os.path.join(BASE_DIR, 'web', 'mobile')

app = Flask(__name__)

@app.route('/')
@app.route('/mobile/')
def mobile():
    return send_from_directory(MOBILE_DIR, 'index.html')

@app.route('/mobile/<path:filename>')
def mobile_files(filename):
    return send_from_directory(MOBILE_DIR, filename)

@app.route('/api/agent/chat', methods=['POST'])
def chat():
    from core.agents.builtin.orchestrator import OrchestratorAgent
    data = request.json
    message = data.get('message', '')
    user_id = data.get('user_id', 'mobile_user')
    
    orch = OrchestratorAgent(user_id)
    result = orch.auto_dispatch(message)
    
    return jsonify({
        "response": result.get('result', {}).get('response', '处理完成')
    })

@app.route('/api/stream/chat')
def stream_chat():
    from flask import Response
    import json
    import time
    
    message = request.args.get('message', '')
    user_id = request.args.get('user_id', 'mobile_user')
    
    def generate():
        from core.agents.builtin.orchestrator import OrchestratorAgent
        orch = OrchestratorAgent(user_id)
        result = orch.auto_dispatch(message)
        response = result.get('result', {}).get('response', '处理完成')
        
        for char in response:
            yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
            time.sleep(0.03)
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("=" * 50)
    print("📱 移动端服务启动")
    print("=" * 50)
    print(f"移动端目录: {MOBILE_DIR}")
    print(f"文件存在: {os.path.exists(os.path.join(MOBILE_DIR, 'index.html'))}")
    print("=" * 50)
    print("访问地址: http://localhost:5003/mobile/")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5003, debug=True)
