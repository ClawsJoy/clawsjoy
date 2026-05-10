#!/usr/bin/env python3
"""ClawsJoy Agent Gateway - 多模型支持"""

import json
import subprocess
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import yaml
import os

app = Flask(__name__)
CORS(app)

# 加载模型配置
def load_model_config():
    with open('/mnt/d/clawsjoy/config/models.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_model_config()
current_model = config.get('current', 'qwen2.5:7b')

def call_llm(prompt: str, model: str = None) -> str:
    """调用 LLM，支持多模型"""
    model_name = model or current_model
    
    # 查找模型配置
    model_config = None
    for m in config.get('models', []):
        if m.get('name') == model_name and m.get('enabled'):
            model_config = m
            break
    
    if not model_config:
        return f"模型 {model_name} 不可用"
    
    provider = model_config.get('provider')
    
    if provider == 'ollama':
        resp = requests.post(
            f"{model_config['endpoint']}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
    
    elif provider == 'openai':
        # OpenAI 兼容 API
        headers = {
            "Authorization": f"Bearer {model_config.get('api_key')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(f"{model_config['endpoint']}/chat/completions", json=data, headers=headers, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    
    return "调用失败"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    model = data.get('model', current_model)
    response = call_llm(msg, model)
    return jsonify({'message': response, 'model': model, 'success': True})

@app.route('/api/models', methods=['GET'])
def list_models():
    """列出可用模型"""
    models = [{'name': m['name'], 'provider': m['provider'], 'enabled': m['enabled']} 
              for m in config.get('models', [])]
    return jsonify({'models': models, 'current': current_model})

@app.route('/api/switch-model', methods=['POST'])
def switch_model():
    """切换模型"""
    data = request.json
    new_model = data.get('model')
    
    # 验证模型是否存在
    for m in config.get('models', []):
        if m.get('name') == new_model and m.get('enabled'):
            # 更新配置文件
            with open('/mnt/d/clawsjoy/config/models.yaml', 'r') as f:
                full_config = yaml.safe_load(f)
            full_config['current'] = new_model
            with open('/mnt/d/clawsjoy/config/models.yaml', 'w') as f:
                yaml.dump(full_config, f)
            
            global current_model
            current_model = new_model
            return jsonify({'success': True, 'current': new_model})
    
    return jsonify({'success': False, 'error': '模型不存在或未启用'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/terminal/execute', methods=['POST'])
def execute():
    data = request.json
    cmd = data.get('command', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return jsonify({'success': True, 'stdout': result.stdout, 'stderr': result.stderr})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 ClawsJoy Agent Gateway (多模型支持)")
    print(f"📍 当前模型: {current_model}")
    print(f"📍 可用模型: {[m['name'] for m in config.get('models', []) if m.get('enabled')]}")
    print("📍 http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=False)
