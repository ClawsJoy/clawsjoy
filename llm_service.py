#!/usr/bin/env python3
"""LLM 对话服务 - 让 LLM 真正干活"""

import sys
import json
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

sys.path.insert(0, 'core')

from lib.skill_registry_v4 import skill_registry
from lib.config_loader import config

app = Flask(__name__)
CORS(app)

# Ollama 配置
OLLAMA_URL = config.get('llm.endpoint', 'http://127.0.0.1:11434')
MODEL = config.get('llm.default_model', 'qwen2.5:7b')


def call_llm(prompt: str, system: str = "") -> str:
    """调用 LLM"""
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": full_prompt, "stream": False},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
        return f"LLM 错误: {resp.status_code}"
    except Exception as e:
        return f"连接错误: {e}"


def get_skills_description() -> str:
    """获取技能描述"""
    desc = []
    for name in skill_registry.skills.keys():
        skill = skill_registry.get_skill(name)
        if skill:
            desc.append(f"- {name}: {skill.description[:100]}")
    return "\n".join(desc)


@app.route('/chat', methods=['POST'])
def chat():
    """LLM 对话接口"""
    data = request.json or {}
    user_message = data.get('message', '')
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "No message"}), 400
    
    # 构建系统提示
    system_prompt = f"""你是一个智能助手，名叫 ClawsJoy。
你可以调用以下技能来帮助用户:
{get_skills_description()}

当用户需要生成图像时，回复格式: [SKILL:ai-image-gen] 然后描述图像需求
当用户需要调度任务时，回复格式: [SKILL:scheduler] 然后描述任务
其他情况正常对话。

记住: 你是一个乐于助人的助手，要友好、热情。"""
    
    # 构建对话上下文
    context = "\n".join([f"用户: {h.get('user', '')}\n助手: {h.get('assistant', '')}" for h in history[-5:]])
    full_prompt = f"{system_prompt}\n\n{context}\n用户: {user_message}\n助手:"
    
    # 调用 LLM
    response = call_llm(full_prompt)
    
    # 检查是否需要调用技能
    if '[SKILL:' in response:
        import re
        match = re.search(r'\[SKILL:(\w+)\](.*)', response)
        if match:
            skill_name = match.group(1)
            skill_prompt = match.group(2).strip()
            
            # 调用技能
            if skill_name == "ai-image-gen":
                result = skill_registry.execute_skill(skill_name, {
                    "prompt": skill_prompt or user_message,
                    "test": False
                })
                if result.get('success'):
                    response = f"✅ 已开始生成图像！{skill_prompt}\n图像将保存到 output 目录。"
                else:
                    response = f"❌ 生成失败: {result.get('error', '未知错误')}"
    
    return jsonify({
        "success": True,
        "response": response,
        "skill_used": skill_name if '[SKILL:' in response else None
    })


@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """流式对话"""
    data = request.json or {}
    user_message = data.get('message', '')
    
    def generate():
        full_prompt = f"用户: {user_message}\n助手:"
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": full_prompt, "stream": True},
            stream=True
        )
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield data.get('response', '')
                except:
                    pass
    
    return Response(generate(), mimetype='text/plain')


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "model": MODEL, "ollama": OLLAMA_URL})


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ClawsJoy LLM 服务")
    print("=" * 50)
    print(f"Ollama: {OLLAMA_URL}")
    print(f"模型: {MODEL}")
    print(f"技能数: {len(skill_registry.skills)}")
    print("=" * 50)
    print("API 端点:")
    print("  POST /chat      - 对话")
    print("  POST /chat/stream - 流式对话")
    print("  GET  /health    - 健康检查")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5012, debug=False)
