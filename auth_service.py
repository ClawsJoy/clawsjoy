#!/usr/bin/env python3
"""用户认证服务 - 多用户支持"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import hashlib
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.environ.get('JWT_SECRET', 'clawsjoy-secret-key-change-in-production')
USERS_DIR = Path("data/users")

# 用户数据库
USERS = {
    "user1": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "name": "管理员",
        "email": "admin@clawsjoy.com",
        "created_at": "2026-05-18"
    },
    "user2": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user",
        "name": "普通用户2",
        "email": "user2@example.com",
        "created_at": "2026-05-18"
    },
    "user3": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user",
        "name": "普通用户3",
        "email": "user3@example.com",
        "created_at": "2026-05-18"
    }
}


@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({"service": "auth_service", "status": "running", "version": "1.0.0"})


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "auth_service"})


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    
    if user_id not in USERS:
        return jsonify({"error": "用户不存在"}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if USERS[user_id]['password_hash'] != password_hash:
        return jsonify({"error": "密码错误"}), 401
    
    token = jwt.encode({
        'user_id': user_id,
        'role': USERS[user_id]['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    # 创建用户专属目录
    user_dir = USERS_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "encrypted").mkdir(exist_ok=True)
    (user_dir / "secrets").mkdir(exist_ok=True)
    (user_dir / "cache").mkdir(exist_ok=True)
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "user_id": user_id,
            "name": USERS[user_id]['name'],
            "role": USERS[user_id]['role']
        }
    })


@app.route('/auth/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "No token"}), 401
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({"valid": True, "user": payload})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@app.route('/auth/users', methods=['GET'])
def list_users():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('role') != 'admin':
            return jsonify({"error": "需要管理员权限"}), 403
    except:
        return jsonify({"error": "无效 token"}), 401
    
    users = [{"user_id": k, "name": v["name"], "role": v["role"]} for k, v in USERS.items()]
    return jsonify({"users": users})


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    name = data.get('name', user_id)
    
    if user_id in USERS:
        return jsonify({"error": "用户已存在"}), 409
    
    USERS[user_id] = {
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "role": "user",
        "name": name,
        "email": data.get('email', ''),
        "created_at": datetime.datetime.now().isoformat()
    }
    
    user_dir = USERS_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    return jsonify({"success": True, "message": "注册成功"})


if __name__ == '__main__':
    print("=" * 50)
    print("🔐 ClawsJoy 认证服务")
    print("=" * 50)
    print("端口: 5444")
    print("健康检查: https://localhost:5444/health")
    print("用户: user1/admin123 (管理员)")
    print("用户: user2/user123 (普通用户)")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5444, debug=False, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
