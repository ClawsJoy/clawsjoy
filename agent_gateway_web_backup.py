#!/usr/bin/env python3
"""ClawsJoy 网关 - 干净版"""

import json
import requests
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import bcrypt
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')

app = Flask(__name__, static_folder='web')
CORS(app)

SECRET_KEY = "clawsjoy-secret-2026"

def hash_password(pwd): return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
def verify_password(pwd, hashed): return bcrypt.checkpw(pwd.encode(), hashed.encode())

def generate_token(user_id, tenant_id, role):
    return jwt.encode({'user_id': user_id, 'tenant_id': tenant_id, 'role': role, 'exp': datetime.utcnow().timestamp() + 86400}, SECRET_KEY)

def verify_token(token):
    try: return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except: return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401
        payload = verify_token(auth[7:])
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

users_dir = Path("data/users")
users_dir.mkdir(parents=True, exist_ok=True)

def get_user(tenant, username):
    f = users_dir / f"{tenant}_{username}.json"
    if f.exists():
        with open(f, 'r') as fp: return json.load(fp)
    return None

def save_user(tenant, username, data):
    with open(users_dir / f"{tenant}_{username}.json", 'w') as f:
        json.dump(data, f, indent=2)

# ========== 基础 API ==========
@app.route('/')
def index(): return send_from_directory('web', 'dashboard.html')
@app.route('/<path:path>')
def static_files(path): return send_from_directory('web', path)

@app.route('/api/health', methods=['GET'])
def health(): return jsonify({'status': 'ok'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    u = data.get('username')
    if get_user('demo', u):
        return jsonify({'success': False, 'error': 'User exists'})
    save_user('demo', u, {
        'username': u,
        'password_hash': hash_password(data.get('password', '')),
        'balance': 0,
        'purchases': [],
        'created_at': datetime.now().isoformat()
    })
    return jsonify({'success': True})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = get_user('demo', data.get('username'))
    if not user or not verify_password(data.get('password', ''), user['password_hash']):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    token = generate_token(data.get('username'), 'demo', 'user')
    return jsonify({'success': True, 'token': token, 'balance': user.get('balance', 0)})

@app.route('/api/user/balance', methods=['GET'])
@require_auth
def balance():
    user = get_user('demo', request.user['user_id'])
    return jsonify({'balance': user.get('balance', 0) if user else 0})

@app.route('/api/user/recharge', methods=['POST'])
@require_auth
def recharge():
    amount = request.json.get('amount', 0)
    user = get_user('demo', request.user['user_id'])
    if not user: return jsonify({'error': 'User not found'}), 404
    user['balance'] = user.get('balance', 0) + amount
    save_user('demo', request.user['user_id'], user)
    return jsonify({'success': True, 'balance': user['balance']})

@app.route('/api/user/purchases', methods=['GET'])
@require_auth
def purchases():
    user = get_user('demo', request.user['user_id'])
    return jsonify({'purchases': user.get('purchases', []) if user else []})

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace():
    products = []
    mp = Path("marketplace/skills")
    if mp.exists():
        for d in mp.iterdir():
            mf = d / "manifest.json"
            if mf.exists():
                with open(mf, 'r') as f:
                    products.append(json.load(f))
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/purchase/<skill>', methods=['POST'])
@require_auth
def purchase(skill):
    user = get_user('demo', request.user['user_id'])
    if not user: return jsonify({'error': 'User not found'}), 404
    if user.get('balance', 0) < 0.99:
        return jsonify({'error': 'Insufficient balance'}), 402
    user['balance'] -= 0.99
    purchases_list = user.get('purchases', [])
    purchases_list.append({'skill': skill, 'price': 0.99, 'time': datetime.now().isoformat()})
    user['purchases'] = purchases_list
    save_user('demo', request.user['user_id'], user)
    return jsonify({'success': True, 'balance': user['balance']})

# ========== 大脑 v2 API ==========
from agent_core.brain_enhanced import brain

@app.route('/api/brain/v2/stats', methods=['GET'])
def brain_v2_stats():
    return jsonify(brain.get_stats())

# ========== 文件处理 API（代理到独立服务）==========
@app.route('/api/file/list', methods=['GET'])
def file_list():
    try:
        resp = requests.get('http://localhost:5003/files', timeout=5)
        return jsonify(resp.json())
    except:
        return jsonify({'files': [], 'count': 0})

# ========== 多智能体 API（代理到独立服务）==========
@app.route('/api/multi/agents', methods=['GET'])
def multi_agents():
    try:
        resp = requests.get('http://localhost:5006/agents', timeout=5)
        return jsonify(resp.json())
    except:
        return jsonify({'agents': []})

@app.route('/api/multi/execute', methods=['POST'])
def multi_execute():
    try:
        resp = requests.post('http://localhost:5006/execute', json=request.json, timeout=30)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({'error': str(e), 'results': {}})

# ========== 聊天 API ==========
@app.route('/api/chat', methods=['POST'])
def chat():
    # 记录到大脑
    from agent_core.brain_enhanced import brain
    brain.record_experience(
        agent=f"user_{request.json.get("user_id", "unknown")}",
        action=msg[:100],
        result={"success": True},
        context="chat"
    )
    data = request.json
    msg = data.get('message', '')
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    try:
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        return jsonify({'message': resp.json().get('response', '')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('\n' + '='*50)
    print('✅ ClawsJoy 网关启动')
    print('='*50)
    print('访问: http://localhost:5002')
    print('='*50)
    app.run(host='0.0.0.0', port=5002, debug=False)

# 增强聊天 API，带大脑记录
@app.route('/api/chat/learn', methods=['POST'])
def chat_with_learning():
    data = request.json
    msg = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')
    
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    
    try:
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        response = resp.json().get('response', '')
        
        # 记录到大脑
        from agent_core.brain_enhanced import brain
        brain.record_experience(
            agent=f"user_{user_id}",
            action=msg[:100],
            result={"success": True, "response": response[:100]},
            context=f"chat"
        )
        
        return jsonify({'message': response, 'recorded': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== 带学习的聊天 API ==========
from agent_core.brain_enhanced import brain

@app.route('/api/chat/learn', methods=['POST'])
def chat_with_learning():
    data = request.json
    msg = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')
    
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    
    try:
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        response = resp.json().get('response', '')
        
        # 记录到大脑
        brain.record_experience(
            agent=f"user_{user_id}",
            action=msg[:100],
            result={"success": True, "response": response[:100]},
            context=f"chat"
        )
        
        return jsonify({'message': response, 'recorded': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
