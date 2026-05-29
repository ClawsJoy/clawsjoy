#!/usr/bin/env python3
"""智能体 Web 服务"""

from flask import Flask, request, jsonify, render_template_string
from core.agent.true_learner import true_learner

app = Flask(__name__)

HTML = '''
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
        .skill { color: gray; font-size: 12px; }
        input { width: 80%; padding: 10px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>🤖 ClawsJoy 智能体</h1>
    <div id="chat"></div>
    <input type="text" id="input" placeholder="输入消息..." />
    <button onclick="send()">发送</button>
    
    <script>
        function send() {
            var input = document.getElementById('input');
            var msg = input.value;
            if (!msg) return;
            
            var chat = document.getElementById('chat');
            chat.innerHTML += '<div class="user">👤 用户: ' + msg + '</div>';
            input.value = '';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            })
            .then(res => res.json())
            .then(data => {
                chat.innerHTML += '<div class="bot">🤖 智能体: ' + data.response + '</div>';
                if (data.skill) {
                    chat.innerHTML += '<div class="skill">📊 使用技能: ' + data.skill + '</div>';
                }
                chat.scrollTop = chat.scrollHeight;
            });
        }
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message"}), 400
    
    result = true_learner.process(message)
    
    return jsonify({
        "success": result.get('success', False),
        "response": result.get('response', ''),
        "skill": result.get('skill'),
        "reasoning": result.get('reasoning')
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(true_learner.get_stats())


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ClawsJoy 智能体服务")
    print("=" * 50)
    print(f"访问: f"http://{config_loader.get("endpoints.gateway.host", "localhost")}:{config_loader.get("endpoints.web_learner.port", 5011)}"")
    print("=" * 50)
    app.run(host='0.0.0.0', port=smart_config.PORTS.get("web", 5011), debug=False)
