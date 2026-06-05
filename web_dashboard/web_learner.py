#!/usr/bin/env python3
"""智能体 Web 服务"""

from flask import Flask, jsonify, render_template_string, request

from core.agent.true_learner import true_learner
from core.lib.unified_config import unified_config

app = Flask(__name__)

# 配置加载器
config_loader = unified_config
smart_config = unified_config

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ClawsJoy 智能体</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        #chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        .user { color: blue; margin: 5px 0; }
        .bot { color: green; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>🤖 ClawsJoy 智能体</h1>
    <div id="chat"></div>
    <input type="text" id="input" placeholder="输入消息..." style="width: 80%; padding: 10px;">
    <button onclick="send()">发送</button>
    <script>
        function send() {
            var input = document.getElementById('input');
            var msg = input.value;
            if (!msg) return;
            addMessage('user', msg);
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            })
            .then(res => res.json())
            .then(data => addMessage('bot', data.response))
            .catch(err => addMessage('bot', '错误: ' + err));
            input.value = '';
        }
        function addMessage(role, text) {
            var chat = document.getElementById('chat');
            var div = document.createElement('div');
            div.className = role;
            div.textContent = (role === 'user' ? '👤 ' : '🤖 ') + text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'response': '请输入消息', 'success': False})
    
    # 调用 true_learner
    result = true_learner.learn(message)
    response = result.get('response', '处理完成')
    
    return jsonify({'response': response, 'success': True})


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ClawsJoy 智能体服务")
    print("=" * 50)
    
    # 获取配置
    gateway_host = config_loader.get("endpoints.gateway.host", "localhost")
    web_port = smart_config.get("endpoints.web_learner.port", 5011)
    
    print(f"访问: http://{gateway_host}:{web_port}")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=web_port, debug=False)
