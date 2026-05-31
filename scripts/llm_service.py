#!/usr/bin/env python3
"""LLM Service - 强制使用系统记忆"""

import sys
import json
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from core.lib.unified_config import unified_config

app = Flask(__name__)
CORS(app)

OLLAMA_URL = unified_config.get("llm.endpoint", "http://localhost:11434")
MODEL = unified_config.get("llm.fast_model", "qwen2.5:3b")


def call_llm(prompt: str) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"num_predict": 200}},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except Exception as e:
        print(f"LLM 错误: {e}")
    return "抱歉，我暂时无法回答。"


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')
    memories = data.get('memories', [])
    
    if not user_message:
        return jsonify({"error": "No message"}), 400
    
    # ===== 系统直接处理，不依赖 LLM =====
    # 问名字
    if '名字' in user_message:
        for m in memories:
            # 查找 "用户说: 我叫XXX" 格式
            match = re.search(r'叫([\u4e00-\u9fa5]{2,4})', m)
            if match:
                name = match.group(1)
                return jsonify({
                    "success": True, 
                    "response": f"您叫 {name} 呀！我记着呢。",
                    "cached": False,
                    "source": "system_memory"
                })
    
    # 问喜好
    if '喜欢' in user_message:
        for m in memories:
            match = re.search(r'喜欢([\u4e00-\u9fa5]+)', m)
            if match:
                pref = match.group(1)
                return jsonify({
                    "success": True,
                    "response": f"您喜欢 {pref} 呀！",
                    "cached": False,
                    "source": "system_memory"
                })
    
    # 其他问题走 LLM
    full_prompt = f"你是 ClawsJoy。用户问: {user_message}\n助手:"
    response = call_llm(full_prompt)
    
    return jsonify({"success": True, "response": response, "cached": False})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    port = 5012
    print(f"🚀 LLM Service 启动, 模型: {MODEL}")
    app.run(host='0.0.0.0', port=port, debug=False)
