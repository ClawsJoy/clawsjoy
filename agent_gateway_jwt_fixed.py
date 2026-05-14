#!/usr/bin/env python3
"""ClawsJoy 网关 - JWT 认证版（无 limiter）"""

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

# 导入模块
from agent_core.auth.jwt_auth import verify_token, generate_token, refresh_token
from agent_core.auth.user_manager import user_manager
from agent_core.billing.manager import billing
from agent_core.monitor.metrics import metrics

# ========== 认证装饰器 ==========
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header[7:]
        payload = verify_token(token)
        if payload.get('error'):
            return jsonify({'error': payload['error']}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated

# ========== 公开 API ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    result = user_manager.register(
        data.get('tenant_id', 'demo'),
        data.get('username', ''),
        data.get('password', ''),
        data.get('email', '')
    )
    return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    result = user_manager.login(
        data.get('tenant_id', 'demo'),
        data.get('username', ''),
        data.get('password', '')
    )
    return jsonify(result)

@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh():
    new_token = refresh_token(request.headers.get('Authorization')[7:])
    if new_token:
        return jsonify({'token': new_token})
    return jsonify({'error': 'Refresh failed'}), 401

# ========== 用户 API ==========
@app.route('/api/user/info', methods=['GET'])
@require_auth
def user_info():
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'username': user['username'],
        'role': user['role'],
        'balance': user.get('balance', 0),
        'tenant_id': request.user['tenant_id']
    })

@app.route('/api/user/balance', methods=['GET'])
@require_auth
def user_balance():
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    return jsonify({'balance': user.get('balance', 0) if user else 0})

# ========== 大脑 API ==========
@app.route('/api/brain/stats', methods=['GET'])
@require_auth
def brain_stats():
    return jsonify({'total_experiences': 0, 'success_rate': 0})

# ========== 技能 API ==========
@app.route('/api/skills/list', methods=['GET'])
@require_auth
def skills_list():
    return jsonify({'skills': []})

# ========== 商品商店 API ==========
MARKETPLACE_DIR = Path("marketplace/skills")

@app.route('/api/marketplace/list', methods=['GET'])
def marketplace_list():
    products = []
    if MARKETPLACE_DIR.exists():
        for skill_dir in MARKETPLACE_DIR.iterdir():
            manifest_file = skill_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    products.append(json.load(f))
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
@require_auth
def marketplace_purchase(skill_name):
    result = billing.deduct(request.user['tenant_id'], request.user['user_id'], 0.99, f'购买 {skill_name}')
    if not result['success']:
        return jsonify({'error': 'Insufficient balance'}), 402
    
    purchase_file = Path(f"data/purchases/{request.user['tenant_id']}_{request.user['user_id']}.json")
    purchase_file.parent.mkdir(parents=True, exist_ok=True)
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    purchases.append({'skill': skill_name, 'purchased_at': datetime.now().isoformat()})
    with open(purchase_file, 'w') as f:
        json.dump(purchases, f, indent=2)
    
    return jsonify({'success': True, 'balance': result['balance']})

# ========== 静态页面 ==========
@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🦞 ClawsJoy Gateway - JWT 认证版')
    print('='*60)
    print(f'🌐 访问: http://localhost:5002')
    print(f'📝 注册: POST /api/auth/register')
    print(f'🔐 登录: POST /api/auth/login')
    print('='*60)
    app.run(host='0.0.0.0', port=5002, debug=False)

@app.route('/api/user/recharge', methods=['POST'])
@require_auth
def user_recharge():
    data = request.json
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    result = user_manager.add_balance(
        request.user['tenant_id'], 
        request.user['user_id'], 
        amount
    )
    return jsonify({'success': True, 'balance': result['balance']})

@app.route('/api/user/transactions', methods=['GET'])
@require_auth
def user_transactions():
    from agent_core.billing.manager import billing
    transactions = billing.get_transactions(
        request.user['tenant_id'], 
        request.user['user_id']
    )
    return jsonify({'transactions': transactions})

@app.route('/api/user/recharge', methods=['POST'])
@require_auth
def user_recharge():
    data = request.json
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    result = user_manager.add_balance(
        request.user['tenant_id'], 
        request.user['user_id'], 
        amount
    )
    return jsonify({'success': True, 'balance': result['balance']})

@app.route('/api/user/recharge', methods=['POST'])
@require_auth
def user_recharge():
    data = request.json
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    result = user_manager.add_balance(
        request.user['tenant_id'], 
        request.user['user_id'], 
        amount
    )
    return jsonify({'success': True, 'balance': result['balance']})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
@require_auth
def marketplace_purchase(skill_name):
    # 扣费
    result = billing.deduct(request.user['tenant_id'], request.user['user_id'], 0.99, f'购买 {skill_name}')
    if not result['success']:
        return jsonify({'error': 'Insufficient balance'}), 402
    
    # 记录购买到用户文件
    user = user_manager.get_user(request.user['tenant_id'], request.user['user_id'])
    purchases = user.get('purchases', [])
    purchases.append({
        'skill': skill_name,
        'price': 0.99,
        'purchased_at': datetime.now().isoformat()
    })
    user['purchases'] = purchases
    user_file = user_manager.users_dir / f"{request.user['tenant_id']}_{request.user['user_id']}.json"
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    
    return jsonify({'success': True, 'balance': result['balance']})
