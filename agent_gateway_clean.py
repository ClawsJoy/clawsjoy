#!/usr/bin/env python3
"""ClawsJoy 统一网关 - 稳定版"""

import sys
import json
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import jwt
import bcrypt

app = Flask(__name__, static_folder='web')
CORS(app)

SECRET_KEY = "clawsjoy-secret-2026"

def hash_password(pwd): return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
def verify_password(pwd, hashed): return bcrypt.checkpw(pwd.encode(), hashed.encode())

def generate_token(user_id, tenant_id, role):
    return jwt.encode({'user_id': user_id, 'tenant_id': tenant_id, 'role': role, 'exp': datetime.utcnow().timestamp() + 86400}, SECRET_KEY, algorithm='HS256')

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

# 用户管理
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

# API
@app.route('/api/health', methods=['GET'])
def health(): return jsonify({'status': 'ok'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    u = data.get('username')
    if get_user('demo', u):
        return jsonify({'success': False, 'error': 'User exists'})
    save_user('demo', u, {
        'username': u, 'password_hash': hash_password(data.get('password', '')),
        'balance': 0, 'purchases': [], 'created_at': datetime.now().isoformat()
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
    data = request.json
    amount = data.get('amount', 0)
    user = get_user('demo', request.user['user_id'])
    if not user: return jsonify({'error': 'User not found'}), 404
    user['balance'] = user.get('balance', 0) + amount
    save_user('demo', request.user['user_id'], user)
    return jsonify({'success': True, 'balance': user['balance']})

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace():
    products = []
    mp = Path("marketplace/skills")
    if mp.exists():
        for d in mp.iterdir():
            mf = d / "manifest.json"
            if mf.exists():
                with open(mf, 'r') as f: products.append(json.load(f))
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/purchase/<skill>', methods=['POST'])
@require_auth
def purchase(skill):
    user = get_user('demo', request.user['user_id'])
    if not user: return jsonify({'error': 'User not found'}), 404
    if user.get('balance', 0) < 0.99:
        return jsonify({'error': 'Insufficient balance'}), 402
    user['balance'] = user['balance'] - 0.99
    purchases = user.get('purchases', [])
    purchases.append({'skill': skill, 'price': 0.99, 'time': datetime.now().isoformat()})
    user['purchases'] = purchases
    save_user('demo', request.user['user_id'], user)
    return jsonify({'success': True, 'balance': user['balance']})

@app.route('/')
def index(): return send_from_directory('web', 'dashboard.html')
@app.route('/<path:f>')
def stat(f): return send_from_directory('web', f)

@app.route('/api/user/purchases', methods=['GET'])
def user_purchases():
    user = get_user('demo', 'tom')
    return jsonify({'purchases': user.get('purchases', []) if user else []})

if __name__ == '__main__':
    print('\n✅ ClawsJoy 网关启动')
    print('注册: POST /api/auth/register')
    print('登录: POST /api/auth/login')
    app.run(host='0.0.0.0', port=5002, debug=False)
