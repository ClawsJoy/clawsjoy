#!/usr/bin/env python3
"""ClawsJoy 安全版网关 - 多租户隔离"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import hashlib
import json
from pathlib import Path

from agent_core.auth.tenant_auth import tenant_auth

app = Flask(__name__, static_folder='web')
CORS(app)

# ========== 权限验证装饰器 ==========
def require_auth(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header:
                return jsonify({'error': 'Unauthorized'}), 401
            
            # 解析 Basic Auth
            import base64
            try:
                auth_type, auth_str = auth_header.split(' ', 1)
                if auth_type.lower() != 'basic':
                    return jsonify({'error': 'Only Basic auth supported'}), 401
                decoded = base64.b64decode(auth_str).decode()
                tenant_id, rest = decoded.split('|', 1)
                username, password = rest.split(':', 1)
            except:
                return jsonify({'error': 'Invalid auth format'}), 401
            
            user_info = tenant_auth.authenticate(tenant_id, username, password)
            if not user_info:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if required_role:
                role_priority = {'admin': 4, 'tenant_admin': 3, 'user': 2, 'guest': 1}
                if role_priority.get(user_info['role'], 0) < role_priority.get(required_role, 0):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.tenant_id = tenant_id
            request.user_id = username
            request.user_role = user_info['role']
            return f(*args, **kwargs)
        return decorated
    return decorator

# ========== 公开 API ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# ========== 租户管理 API（仅管理员） ==========
@app.route('/api/admin/tenants', methods=['POST'])
@require_auth('admin')
def create_tenant():
    data = request.json
    tenant_id = data.get('tenant_id')
    admin_user = data.get('admin_user')
    admin_pass = data.get('admin_pass')
    result = tenant_auth.create_tenant(tenant_id, admin_user, admin_pass)
    return jsonify(result)

@app.route('/api/admin/tenants/<tenant_id>/users', methods=['POST'])
@require_auth('admin')
def create_user_in_tenant(tenant_id):
    data = request.json
    result = tenant_auth.create_user(tenant_id, data.get('username'), data.get('password'), data.get('role', 'user'))
    return jsonify(result)

# ========== 租户内 API（租户管理员） ==========
@app.route('/api/tenant/users', methods=['POST'])
@require_auth('tenant_admin')
def create_tenant_user():
    data = request.json
    result = tenant_auth.create_user(request.tenant_id, data.get('username'), data.get('password'), 'user')
    return jsonify(result)

@app.route('/api/tenant/stats', methods=['GET'])
@require_auth('tenant_admin')
def tenant_stats():
    tenant_dir = Path(f"data/tenants/{request.tenant_id}")
    user_count = len(list((tenant_dir / "users").glob("*.json"))) if (tenant_dir / "users").exists() else 0
    return jsonify({
        'tenant_id': request.tenant_id,
        'user_count': user_count,
        'current_user': request.user_id
    })

# ========== 用户 API（普通用户） ==========
@app.route('/api/user/data', methods=['GET'])
@require_auth('user')
def user_data():
    user_data_path = tenant_auth.get_user_data_path(request.tenant_id, request.user_id)
    return jsonify({
        'tenant_id': request.tenant_id,
        'user_id': request.user_id,
        'data_path': str(user_data_path),
        'message': f'Welcome {request.user_id}'
    })

# ========== 静态页面 ==========
@app.route('/')
def index():
    return send_from_directory('web', 'dashboard.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('web', filename)

if __name__ == '__main__':
    print('\n' + '='*50)
    print('ClawsJoy 安全版 - 多租户隔离')
    print('='*50)
    print(f'访问: http://localhost:5002')
    print('默认管理员: admin / admin123')
    print('='*50)
    app.run(host='0.0.0.0', port=5002, debug=False)
