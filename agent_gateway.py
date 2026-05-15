#!/usr/bin/env python3
import sys
import json
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/mnt/d/clawsjoy')

app = Flask(__name__, static_folder='web')
CORS(app)

# 导入模块
from agent_core.brain_enhanced import brain
from agent_core.memory_system import openclaw_memory
from agent_core.vector_kb import vector_kb
from skills.skill_interface import skill_registry
from agents.decision_engine import decision_engine

# 注册技能
print("🔄 注册技能...")
from skills.image_collector import skill as img_skill
from skills.script_generator import skill as script_skill
from skills.slideshow_maker import skill as video_skill
from skills.weather_skill import skill as weather
for s in [img_skill, script_skill, video_skill, weather]:
    try:
        skill_registry.register(s)
    except:
        pass

print("✅ 技能注册完成")

# ========== 健康检查 ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# ========== 基础聊天 ==========
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    try:
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        return jsonify({'message': resp.json().get('response', ''), 'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 大脑 API ==========
@app.route('/api/brain/stats', methods=['GET'])
def brain_stats():
    return jsonify(brain.get_stats())

# ========== 记忆 API ==========
@app.route('/api/memory/add', methods=['POST'])
def memory_add():
    data = request.json
    mid = openclaw_memory.add_memory(data.get('content', ''))
    return jsonify({'success': True, 'memory_id': mid})

@app.route('/api/memory/recall', methods=['POST'])
def memory_recall():
    data = request.json
    memories = openclaw_memory.recall(data.get('query', ''), limit=data.get('limit', 5))
    return jsonify({'memories': memories})

# ========== 向量 API ==========
@app.route('/api/vector/stats', methods=['GET'])
def vector_stats():
    return jsonify({'total': vector_kb.count()})

# ========== 商品商店 API ==========
MARKETPLACE_DIR = Path("marketplace/skills")

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace_list():
    products = []
    category = request.args.get('category', '')
    
    if MARKETPLACE_DIR.exists():
        for skill_dir in MARKETPLACE_DIR.iterdir():
            if skill_dir.is_dir():
                manifest_file = skill_dir / "manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                    if not category or manifest.get('category') == category:
                        products.append(manifest)
    
    # 如果没有商品，返回示例
    if not products:
        products = [
            {"name": "image_collector", "category": "content", "description": "图片采集", "price": 0.99},
            {"name": "script_writer", "category": "content", "description": "脚本生成", "price": 1.99},
            {"name": "slideshow_maker", "category": "video", "description": "视频制作", "price": 2.99},
        ]
    
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/categories', methods=['GET'])
def marketplace_categories():
    categories = set()
    if MARKETPLACE_DIR.exists():
        for skill_dir in MARKETPLACE_DIR.iterdir():
            manifest_file = skill_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                    categories.add(manifest.get('category', 'general'))
    
    if not categories:
        categories = ['content', 'video', 'api', 'utility', 'publish']
    
    return jsonify({'categories': list(categories)})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
def marketplace_purchase(skill_name):
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    
    purchase_file = Path(f"data/purchases/{user_id}.json")
    purchase_file.parent.mkdir(parents=True, exist_ok=True)
    
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    
    purchases.append({
        'skill': skill_name,
        'purchased_at': datetime.now().isoformat(),
        'price': 0.99
    })
    
    with open(purchase_file, 'w') as f:
        json.dump(purchases, f, indent=2)
    
    return jsonify({'success': True, 'message': f'成功购买 {skill_name}'})

@app.route('/api/marketplace/my/purchases', methods=['GET'])
def my_purchases():
    user_id = request.args.get('user_id', 'anonymous')
    purchase_file = Path(f"data/purchases/{user_id}.json")
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    return jsonify({'purchases': purchases})

# ========== 安全对话 API ==========
from agent_core.security.user_gate import security_manager

@app.route('/api/security/chat', methods=['POST'])
def security_chat():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    message = data.get('message', '')
    gate = security_manager.get_gate(user_id)
    response, protected = gate.chat(message)
    return jsonify({'user_id': user_id, 'response': response, 'protected_count': len(protected)})

# ========== 技能 API ==========
@app.route('/api/skills/list', methods=['GET'])
def skills_list():
    return jsonify({'skills': skill_registry.get_skill_names()})

@app.route('/api/skills/execute', methods=['POST'])
def skills_execute():
    data = request.json
    skill_name = data.get('skill', '')
    params = data.get('params', {})
    skill = skill_registry.get(skill_name)
    if skill:
        return jsonify(skill.execute(params))
    return jsonify({'error': 'Skill not found'}), 404

# ========== 静态页面 ==========
@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('web', 'dashboard.html')

@app.route('/marketplace')
def marketplace():
    return send_from_directory('web', 'marketplace.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🦞 ClawsJoy Gateway - 商品商店版')
    print('='*50)
    print(f'访问: http://localhost:5002')
    print(f'商店: http://localhost:5002/marketplace')
    print(f'仪表盘: http://localhost:5002/dashboard')
    print('='*50)
    app.run(host='0.0.0.0', port=5002, debug=False)
