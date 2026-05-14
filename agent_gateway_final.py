#!/usr/bin/env python3
"""ClawsJoy 完整版 - 集成所有核心功能"""

import sys
import json
import os
import hashlib
import base64
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, '/mnt/d/clawsjoy')

app = Flask(__name__, static_folder='web')
CORS(app)

# ========== 1. 多租户权限系统 ==========
class TenantAuth:
    def __init__(self, data_dir: str = "data/tenants"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_default()
    
    def _init_default(self):
        system_dir = self.data_dir / "system"
        system_dir.mkdir(exist_ok=True)
        admin_file = system_dir / "admin.json"
        if not admin_file.exists():
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            with open(admin_file, 'w') as f:
                json.dump({'username': 'admin', 'password_hash': admin_hash, 'role': 'admin'}, f)
        
        demo_dir = self.data_dir / "demo"
        demo_dir.mkdir(exist_ok=True)
        for d in ["secrets", "users", "data", "skills"]:
            (demo_dir / d).mkdir(exist_ok=True)
    
    def authenticate(self, auth_header):
        try:
            auth_type, auth_str = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return None
            decoded = base64.b64decode(auth_str).decode()
            parts = decoded.split(':', 1)
            if '|' in parts[0]:
                tenant_id, username = parts[0].split('|', 1)
                password = parts[1]
            else:
                tenant_id = "demo"
                username = parts[0]
                password = parts[1]
            
            tenant_dir = self.data_dir / tenant_id
            if not tenant_dir.exists():
                return None
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            admin_file = tenant_dir / "admin.json"
            if admin_file.exists():
                with open(admin_file, 'r') as f:
                    admin = json.load(f)
                    if admin['username'] == username and admin['password_hash'] == password_hash:
                        return {'user_id': username, 'role': admin['role'], 'tenant_id': tenant_id}
            
            users_dir = tenant_dir / "users"
            for user_file in users_dir.glob("*.json"):
                with open(user_file, 'r') as f:
                    user = json.load(f)
                    if user['username'] == username and user['password_hash'] == password_hash:
                        return {'user_id': username, 'role': user['role'], 'tenant_id': tenant_id}
        except:
            pass
        return None

tenant_auth = TenantAuth()

def require_auth(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return jsonify({'error': 'Unauthorized'}), 401
            user_info = tenant_auth.authenticate(auth_header)
            if not user_info:
                return jsonify({'error': 'Invalid credentials'}), 401
            request.user_info = user_info
            return f(*args, **kwargs)
        return decorated
    return decorator

# ========== 2. 大脑学习系统 ==========
class Brain:
    def __init__(self):
        self.brain_file = Path("data/brain.json")
        self.knowledge = self._load()
    
    def _load(self):
        if self.brain_file.exists():
            with open(self.brain_file, 'r') as f:
                return json.load(f)
        return {"experiences": [], "stats": {"total": 0, "success_rate": 0}}
    
    def _save(self):
        with open(self.brain_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def record_experience(self, agent, action, result):
        self.knowledge["experiences"].append({
            "agent": agent, "action": action, "result": result, "timestamp": datetime.now().isoformat()
        })
        self.knowledge["stats"]["total"] = len(self.knowledge["experiences"])
        successes = sum(1 for e in self.knowledge["experiences"] if e.get("result", {}).get("success"))
        self.knowledge["stats"]["success_rate"] = successes / max(1, len(self.knowledge["experiences"]))
        self._save()
    
    def get_stats(self):
        return self.knowledge["stats"]

brain = Brain()

# ========== 3. 商品商店 ==========
MARKETPLACE_DIR = Path("marketplace/skills")

@app.route('/api/marketplace/list', methods=['GET'])
@require_auth()
def marketplace_list():
    products = []
    if MARKETPLACE_DIR.exists():
        for skill_dir in MARKETPLACE_DIR.iterdir():
            manifest_file = skill_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    products.append(json.load(f))
    if not products:
        products = [{"name": "image_collector", "category": "content", "price": 0.99}]
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/marketplace/purchase/<skill_name>', methods=['POST'])
@require_auth()
def marketplace_purchase(skill_name):
    purchase_file = Path(f"data/purchases/{request.user_info['tenant_id']}_{request.user_info['user_id']}.json")
    purchase_file.parent.mkdir(parents=True, exist_ok=True)
    purchases = []
    if purchase_file.exists():
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    purchases.append({'skill': skill_name, 'purchased_at': datetime.now().isoformat()})
    with open(purchase_file, 'w') as f:
        json.dump(purchases, f, indent=2)
    brain.record_experience("marketplace", f"purchase_{skill_name}", {"success": True})
    return jsonify({'success': True, 'message': f'购买成功'})

# ========== 4. 基础 API ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/brain/stats', methods=['GET'])
@require_auth()
def brain_stats():
    return jsonify(brain.get_stats())

@app.route('/api/user/info', methods=['GET'])
@require_auth()
def user_info():
    return jsonify(request.user_info)

# ========== 5. 静态页面 ==========
@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/marketplace')
def marketplace():
    return send_from_directory('web', 'marketplace.html')

@app.route('/admin')
def admin():
    return send_from_directory('web', 'admin.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

# ========== 启动 ==========
if __name__ == '__main__':
    print('\n' + '='*60)
    print('🦞 ClawsJoy 完整版 - 多租户隔离 | 大脑学习 | 商品商店')
    print('='*60)
    print(f'🌐 访问: http://localhost:5002')
    print(f'🔐 默认账号: demo|admin / admin123')
    print('='*60)
    app.run(host='0.0.0.0', port=5002, debug=False)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per minute"])

@app.route('/api/skills/execute', methods=['POST'])
@limiter.limit("30 per minute")
def skills_execute():
    # 技能执行逻辑
    pass
