#!/usr/bin/env python3
#!/usr/bin/env python3
"""Unified Service - Unified Service 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import json
import sys

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

sys.path.insert(0, "core")

from core.agent.smart_agent import smart_agent as config_agent
from lib.config_loader import config
from core.lib.skill_registry_v6 import skill_registry

app = Flask(__name__)
CORS(app)

# 读取配置
WEB_PORT = config.get("ports.web", 5011)
LLM_PORT = config.get("llm.ports.llm_service", 5012)


# HTML 界面
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ClawsJoy 智能助手</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        #chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        .user { color: blue; margin: 5px 0; }
        .bot { color: green; margin: 5px 0; }
        input { width: 80%; padding: 10px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>🤖 ClawsJoy 智能助手</h1>
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
                chat.innerHTML += '<div class="bot">🤖 助手: ' + data.response + '</div>';
                chat.scrollTop = chat.scrollHeight;
            });
        }
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Web 界面"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def chat():
    """对话接口 - 使用配置驱动 Agent"""
    data = request.json or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "No message"}), 400

    result = config_agent.process(message)

    return jsonify(
        {
            "success": result.get("success", False),
            "response": result.get("response", ""),
            "skill": result.get("skill"),
            "params": result.get("params"),
        }
    )


@app.route("/api/skills", methods=["GET"])
def list_skills():
    """列出所有技能"""
    return jsonify(
        {
            "skills": list(skill_registry.skills.keys()),
            "total": len(skill_registry.skills),
        }
    )


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify(
        {
            "status": "ok",
            "version": "4.0.0",
            "agent": config_agent.VERSION,
            "ollama": config_agent.ollama_url,
            "model": config_agent.default_model,
        }
    )


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ClawsJoy 统一服务")
    print("=" * 50)
    print(f"Web 界面: http://localhost:{WEB_PORT}")
    print(f"API 地址: http://localhost:{WEB_PORT}/api/chat")
    print(f"技能列表: http://localhost:{WEB_PORT}/api/skills")
    print("=" * 50)
    print(f"Ollama: {config_agent.ollama_url}")
    print(f"模型: {config_agent.default_model}")
    print(f"技能数: {len(skill_registry.skills)}")
    print("=" * 50)

    app.run(host="0.0.0.0", port=WEB_PORT, debug=False)
