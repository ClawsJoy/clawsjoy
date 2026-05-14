#!/usr/bin/env python3
"""ClawsJoy Agent Gateway - 智能路由版"""

import json
import subprocess
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import yaml
import os
import re

app = Flask(__name__)
CORS(app)

# 加载模型配置
def load_model_config():
    with open('/mnt/d/clawsjoy/config/models.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_model_config()

# 智能路由规则
ROUTING_RULES = {
    "simple": {
        "keywords": ["天气", "时间", "日期", "hello", "hi", "你好", "简单", "ping"],
        "model": "qwen2.5:3b"
    },
    "code": {
        "keywords": ["代码", "编程", "python", "docker", "bash", "修复", "bug", "错误", "重启"],
        "model": "qwen2.5:7b"
    },
    "complex": {
        "keywords": ["分析", "架构", "设计", "优化", "安全", "策略", "方案"],
        "model": "qwen2.5:7b"
    },
    "knowledge": {
        "keywords": ["clawsjoy", "功能", "是什么", "怎么用", "介绍"],
        "model": "qwen2.5:7b"
    }
}

def auto_select_model(message: str) -> str:
    """智能选择模型"""
    msg_lower = message.lower()
    
    # 检查规则
    for intent, rule in ROUTING_RULES.items():
        for keyword in rule["keywords"]:
            if keyword in msg_lower:
                print(f"   🧠 路由: {intent} → {rule['model']}")
                return rule["model"]
    
    # 默认
    return "qwen2.5:7b"

def call_llm(prompt: str, model: str = None) -> str:
    """调用 LLM"""
    if model is None:
        model = config.get('current', 'qwen2.5:7b')
    
    # 查找模型配置
    model_config = None
    for m in config.get('models', []):
        if m.get('name') == model and m.get('enabled'):
            model_config = m
            break
    
    if not model_config or model_config.get('provider') != 'ollama':
        return f"模型 {model} 不可用"
    
    try:
        resp = requests.post(
            f"{model_config['endpoint']}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except Exception as e:
        print(f"LLM 错误: {e}")
    
    return "调用失败"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    
    # 自动选择模型
    auto_model = auto_select_model(msg)
    
    # 先检索知识库
    from agent_core.simple_vector import simple_vector
    from agent_core.brain_connector import brain_connector
    
    results = simple_vector.search(msg, top_k=3)
    knowledge = []
    for r in results:
        if r['score'] > 0.3:
            knowledge.append(r['text'][:500])
    
    if knowledge:
        context = '\n\n'.join(knowledge[:3])
        prompt = f"""基于以下知识回答用户问题。

知识库内容:
{context}

用户问题: {msg}

请基于以上知识回答。"""
        response = call_llm(prompt, auto_model)
    else:
        response = call_llm(f"请回答：{msg}", auto_model)
    
    return jsonify({
        'message': response,
        'model': auto_model,
        'routed': True,
        'success': True
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    models = [{'name': m['name'], 'provider': m['provider'], 'enabled': m['enabled']} 
              for m in config.get('models', [])]
    return jsonify({'models': models, 'current': config.get('current')})

@app.route('/api/switch-model', methods=['POST'])
def switch_model():
    data = request.json
    new_model = data.get('model')
    for m in config.get('models', []):
        if m.get('name') == new_model and m.get('enabled'):
            with open('/mnt/d/clawsjoy/config/models.yaml', 'r') as f:
                full_config = yaml.safe_load(f)
            full_config['current'] = new_model
            with open('/mnt/d/clawsjoy/config/models.yaml', 'w') as f:
                yaml.dump(full_config, f)
            return jsonify({'success': True, 'current': new_model})
    return jsonify({'success': False, 'error': '模型不存在'})

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



# ========== 运营管理 API ==========
def dashboard():
    from flask import send_from_directory
    return send_from_directory('web', 'dashboard.html')

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🦞 ClawsJoy Gateway")
    print("=" * 50)
    print("访问: http://localhost:5002/dashboard.html")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5002, debug=False)

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('web', 'dashboard.html')

# 修改购买函数，添加大脑记录

# ========== 商品商店 API ==========
import json
from pathlib import Path


    """列出所有可购买商品"""
    category = request.args.get('category', '')
    products = []
    
    for skill_dir in MARKETPLACE_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        manifest_file = skill_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            if not category or manifest.get('category') == category:
                products.append(manifest)
    
    return jsonify({'products': products, 'total': len(products)})

    """获取所有商品类别"""
    categories = set()
    for skill_dir in MARKETPLACE_DIR.iterdir():
        manifest_file = skill_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                categories.add(manifest.get('category', 'general'))
    
    return jsonify({'categories': list(categories)})

    """购买技能"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    
    skill_dir = MARKETPLACE_DIR / skill_name
    manifest_file = skill_dir / "manifest.json"
    
    if not manifest_file.exists():
        return jsonify({'success': False, 'error': 'Skill not found'}), 404
    
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    # 记录购买
    purchase_file = Path(f"data/purchases/{user_id}.json")
    purchase_file.parent.mkdir(parents=True, exist_ok=True)
    
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    
    purchases.append({
        'skill': skill_name,
        'price': manifest.get('price', 0.99),
        'purchased_at': datetime.now().isoformat()
    })
    
    with open(purchase_file, 'w') as f:
        json.dump(purchases, f, indent=2)
    
    return jsonify({
        'success': True,
        'message': f'Successfully purchased {manifest.get("name", skill_name)}',
        'price': manifest.get('price', 0.99)
    })

    """获取用户已购商品"""
    user_id = request.args.get('user_id', 'anonymous')
    purchase_file = Path(f"data/purchases/{user_id}.json")
    
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    
    return jsonify({'purchases': purchases, 'total': len(purchases)})




    from flask import send_from_directory

    from flask import send_from_directory

    from flask import send_from_directory

    import os
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/shop')
def shop():
    with open('web/marketplace.html', 'r', encoding='utf-8') as f:
        return f.read()
