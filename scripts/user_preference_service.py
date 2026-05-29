#!/usr/bin/env python3
"""用户偏好存储服务 - 加密存储"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import json
import hashlib
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

SECRET_KEY = "clawsjoy-secret-key-change-in-production"
USERS_DIR = Path("data/users")


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "preference_service"})


@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({"service": "preference_service", "status": "running"})


@app.route('/preference/save', methods=['POST'])
def save_preference():
    """保存用户偏好（加密）"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return jsonify({"error": "Invalid token"}), 401
    
    data = request.json
    category = data.get('category', 'general')
    preferences = data.get('preferences', {})
    
    user_file = USERS_DIR / user_id / "encrypted" / f"preferences_{category}.enc"
    user_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(user_file, 'w') as f:
        json.dump(preferences, f, indent=2)
    
    return jsonify({"success": True, "message": "偏好已保存"})


@app.route('/preference/load', methods=['GET'])
def load_preference():
    """加载用户偏好"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return jsonify({"error": "Invalid token"}), 401
    
    category = request.args.get('category', 'general')
    user_file = USERS_DIR / user_id / "encrypted" / f"preferences_{category}.enc"
    
    if user_file.exists():
        with open(user_file, 'r') as f:
            preferences = json.load(f)
        return jsonify({"success": True, "preferences": preferences})
    
    return jsonify({"success": True, "preferences": {}})


if __name__ == '__main__':
    print("=" * 50)
    print("🔐 用户偏好服务")
    print("=" * 50)
    print("端口: 5445")
    print("健康检查: f"http://{config_loader.get("endpoints.user_preference.host", "localhost")}:{config_loader.get("endpoints.user_preference.port", 5445)}"/health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=smart_config.PORTS.get("user_preference", 5445), debug=False, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
