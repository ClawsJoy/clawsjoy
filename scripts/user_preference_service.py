import os

#!/usr/bin/env python3
#!/usr/bin/env python3
"""User Preference Service - User Preference Service 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.getenv("JWT_SECRET", "change-me")
USERS_DIR = Path("data/users")


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "preference_service"})


@app.route("/", methods=["GET"])
def index():
    """根路径"""
    return jsonify({"service": "preference_service", "status": "running"})


@app.route("/preference/save", methods=["POST"])
def save_preference():
    """保存用户偏好（加密）"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 401

    data = request.json
    category = data.get("category", "general")
    preferences = data.get("preferences", {})

    user_file = USERS_DIR / user_id / "encrypted" / f"preferences_{category}.enc"
    user_file.parent.mkdir(parents=True, exist_ok=True)

    with open(user_file, "w") as f:
        json.dump(preferences, f, indent=2)

    return jsonify({"success": True, "message": "偏好已保存"})


@app.route("/preference/load", methods=["GET"])
def load_preference():
    """加载用户偏好"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 401

    category = request.args.get("category", "general")
    user_file = USERS_DIR / user_id / "encrypted" / f"preferences_{category}.enc"

    if user_file.exists():
        with open(user_file, "r") as f:
            preferences = json.load(f)
        return jsonify({"success": True, "preferences": preferences})

    return jsonify({"success": True, "preferences": {}})


if __name__ == "__main__":
    print("=" * 50)
    print("🔐 用户偏好服务")
    print("=" * 50)
    print("端口: 5445")
    print(
        f"健康检查: http://{config_loader.get("endpoints.user_preference.host", "localhost")}:{config_loader.get("endpoints.user_preference.port", 5445)}/health"
    )
    print("=" * 50)
    app.run(
        host="0.0.0.0",
        port=smart_config.PORTS.get("user_preference", 5445),
        debug=False,
        ssl_context=("ssl/cert.pem", "ssl/key.pem"),
    )
