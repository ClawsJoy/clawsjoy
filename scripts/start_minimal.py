"""最小化启动 - 仅测试核心功能"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"service": "gateway", "status": "ok", "version": "5.0"})

@app.route('/api/butler/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    # 简单的规则响应
    if "你好" in message or "hello" in message.lower():
        response = "您好！我是您的私人管家，有什么可以帮您的？"
    elif "名字" in message or "叫什么" in message:
        response = "我是您的小管家，您可以叫我小管~"
    else:
        response = f"收到您的消息：{message}"
    
    return jsonify({"success": True, "response": response, "user_id": user_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
