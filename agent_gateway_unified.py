#!/usr/bin/env python3
"""ClawsJoy 统一网关 - 完整版"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, '/mnt/d/clawsjoy')

app = Flask(__name__, static_folder='web')
CORS(app)

# ========== 1. JWT 认证模块 ==========
import jwt
import bcrypt

SECRET_KEY = "clawsjoy-secret-key-2026"
TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id: str, tenant_id: str, role: str) -> str:
    payload = {
        'user_id': user_id, 'tenant_id': tenant_id, 'role': role,
        'exp': datetime.utcnow().timestamp() + TOKEN_EXPIRE_HOURS * 3600,
        'iat': datetime.utcnow().timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except:
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401
        token = auth_header[7:]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

# ========== 2. 用户管理 ==========
class UserManager:
    def __init__(self):
        self.users_dir = Path("data/users")
        self.users_dir.mkdir(parents=True, exist_ok=True)
    
    def register(self, tenant_id: str, username: str, password: str, email: str = "") -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if user_file.exists():
            return {'success': False, 'error': 'User exists'}
        user = {
            'username': username, 'password_hash': hash_password(password),
            'email': email, 'tenant_id': tenant_id, 'role': 'user',
            'created_at': datetime.now().isoformat(), 'balance': 0,
            'purchases': [], 'skills': []
        }
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
        return {'success': True, 'username': username}
    
    def login(self, tenant_id: str, username: str, password: str) -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if not user_file.exists():
            return {'success': False, 'error': 'User not found'}
        with open(user_file, 'r') as f:
            user = json.load(f)
        if not verify_password(password, user['password_hash']):
            return {'success': False, 'error': 'Invalid password'}
        token = generate_token(username, tenant_id, user['role'])
        return {'success': True, 'token': token, 'user': {'username': username, 'role': user['role'], 'balance': user.get('balance', 0)}}
    
    def get_user(self, tenant_id: str, username: str) -> dict:
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        if user_file.exists():
            with open(user_file, 'r') as f:
                return json.load(f)
        return None
    
    def add_balance(self, tenant_id: str, username: str, amount: float) -> dict:
        user = self.get_user(tenant_id, username)
        if not user:
            return {'success': False, 'error': 'User not found'}
        user['balance'] = user.get('balance', 0) + amount
        user_file = self.users_dir / f"{tenant_id}_{username}.json"
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
        return {'success': True, 'balance': user['balance']}

user_manager = UserManager()

# ========== 3. 计费模块 ==========
def deduct_balance(tenant_id: str, user_id: str, amount: float, reason: str) -> dict:
    user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
    if not user_file.exists():
        return {'success': False, 'error': 'User not found'}
    with open(user_file, 'r') as f:
        user = json.load(f)
    current = user.get('balance', 0)
    if current < amount:
        return {'success': False, 'error': 'Insufficient balance', 'balance': current}
    user['balance'] = current - amount
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    return {'success': True, 'balance': user['balance']}

# ========== 4. API 路由 ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    result = user_manager.register(data.get('tenant_id', 'demo'), data.get('username', ''), data.get('password', ''), data.get('email', ''))
    return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    result = user_manager.login(data.get('tenant_id', 'demo'), data.get('username', ''), data.get('password', ''))
    return jsonify(result)

@app.route('/api/user/info', methods=['GET'])
@require_auth
def user_info():
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    return jsonify({'username': user['username'], 'role': user['role'], 'balance': user.get('balance', 0), 'tenant_id': request.user['tenant_id']})

@app.route('/api/user/balance', methods=['GET'])
@require_auth
def user_balance():
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    return jsonify({'balance': user.get('balance', 0) if user else 0})

@app.route('/api/user/recharge', methods=['POST'])
@require_auth
def user_recharge():
    data = request.json
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    result = user_manager.add_balance(request.user['tenant_id'], request.user['user_id'], amount)
    return jsonify({'success': True, 'balance': result['balance']})

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace_list():
    marketplace_dir = Path("marketplace/skills")
    products = []
    if marketplace_dir.exists():
        for skill_dir in marketplace_dir.iterdir():
            manifest_file = skill_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    products.append(json.load(f))
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
@require_auth
def marketplace_purchase(skill_name):
    result = deduct_balance(request.user['tenant_id'], request.user['user_id'], 0.99, f'购买 {skill_name}')
    if not result['success']:
        return jsonify({'error': result['error']}), 402
    
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    purchases = user.get('purchases', [])
    purchases.append({'skill': skill_name, 'price': 0.99, 'purchased_at': datetime.now().isoformat()})
    user['purchases'] = purchases
    user_file = Path(f"data/users/{request.user['tenant_id']}_{request.user['user_id']}.json")
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    
    return jsonify({'success': True, 'balance': result['balance']})

@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

@app.route(/api/user/transactions, methods=[GET])
@require_auth
def get_transactions():
    trans_file = Path(f"data/transactions/{request.user["tenant_id"]}_{request.user["user_id"]}.json")
    if trans_file.exists():
        with open(trans_file, "r") as f:
            transactions = json.load(f)
        return jsonify({"transactions": transactions[-50:]})
    return jsonify({"transactions": []})

@app.route(/api/user/transactions, methods=[GET])
@require_auth
def get_transactions():
    trans_file = Path(f"data/transactions/{request.user["tenant_id"]}_{request.user["user_id"]}.json")
    if trans_file.exists():
        with open(trans_file, "r") as f:
            transactions = json.load(f)
        return jsonify({"transactions": transactions[-50:]})
    return jsonify({"transactions": []})

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🦞 ClawsJoy 统一网关 - 完整版')
    print('='*60)
    print(f'🌐 访问: http://localhost:5002')
    print(f'📝 注册: POST /api/auth/register')
    print(f'🔐 登录: POST /api/auth/login')
    print('='*60)
    app.run(host='0.0.0.0', port=5002, debug=False)

# 交易记录文件
def record_transaction(tenant_id: str, user_id: str, amount: float, reason: str, balance: float):
    trans_dir = Path("data/transactions")
    trans_dir.mkdir(parents=True, exist_ok=True)
    trans_file = trans_dir / f"{tenant_id}_{user_id}.json"
    
    transactions = []
    if trans_file.exists():
        with open(trans_file, 'r') as f:
            transactions = json.load(f)
    
    transactions.append({
        'amount': amount,
        'reason': reason,
        'balance': balance,
        'timestamp': datetime.now().isoformat()
    })
    
    with open(trans_file, 'w') as f:
        json.dump(transactions[-100:], f, indent=2)

# 修改 deduct_balance，自动记录
def deduct_balance(tenant_id: str, user_id: str, amount: float, reason: str) -> dict:
    user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
    if not user_file.exists():
        return {'success': False, 'error': 'User not found'}
    
    with open(user_file, 'r') as f:
        user = json.load(f)
    
    current = user.get('balance', 0)
    if current < amount:
        return {'success': False, 'error': 'Insufficient balance', 'balance': current}
    
    new_balance = current - amount
    user['balance'] = new_balance
    
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    
    # 自动记录交易
    record_transaction(tenant_id, user_id, -amount, reason, new_balance)
    
    return {'success': True, 'balance': new_balance}

# 充值也自动记录
def add_balance(tenant_id: str, user_id: str, amount: float, reason: str = "recharge") -> dict:
    user_file = Path(f"data/users/{tenant_id}_{user_id}.json")
    if not user_file.exists():
        return {'success': False, 'error': 'User not found'}
    
    with open(user_file, 'r') as f:
        user = json.load(f)
    
    new_balance = user.get('balance', 0) + amount
    user['balance'] = new_balance
    
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    
    # 自动记录交易
    record_transaction(tenant_id, user_id, amount, reason, new_balance)
    
    return {'success': True, 'balance': new_balance}

@app.route('/api/user/transactions', methods=['GET'])
@require_auth
def user_transactions():
    trans_file = Path(f"data/transactions/{request.user['tenant_id']}_{request.user['user_id']}.json")
    if trans_file.exists():
        with open(trans_file, 'r') as f:
            transactions = json.load(f)
        return jsonify({'transactions': transactions[-50:]})
    return jsonify({'transactions': []})

@app.route('/api/user/transactions', methods=['GET'])
@require_auth
def get_transactions():
    trans_file = Path(f"data/transactions/{request.user['tenant_id']}_{request.user['user_id']}.json")
    if trans_file.exists():
        with open(trans_file, 'r') as f:
            transactions = json.load(f)
        return jsonify({'transactions': transactions[-50:]})
    return jsonify({'transactions': []})
