#!/usr/bin/env python3
"""ClawsJoy 安全 Web Dashboard"""

from datetime import datetime
from functools import wraps

import jwt
import psutil
import requests
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = "clawsjoy-secret-key-change-in-production"
AUTH_SERVICE = "https://localhost:5444"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            resp = requests.get(
                f"{AUTH_SERVICE}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                verify=False,
                timeout=5,
            )
            if resp.status_code != 200:
                return jsonify({"error": "Invalid token"}), 401
            request.user = resp.json().get("user", {})
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def index():
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head><title>ClawsJoy 安全仪表板</title><meta charset="utf-8"></head>
    <body>
        <h1>🔒 ClawsJoy 安全仪表板</h1>
        <p>服务运行中</p>
        <p><a href="/api/health">健康检查</a> | <a href="/api/services">服务状态</a></p>
    </body>
    </html>
    """
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """系统健康检查"""
    from lib.agent_registry import agent_registry
    from core.lib.skill_registry_v6 import skill_registry

    system = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }

    agents = agent_registry.get_stats() if agent_registry else {"total": 0, "active": 0}
    skills = len(skill_registry.skills) if hasattr(skill_registry, "skills") else 0

    health_score = 100
    if system["cpu_percent"] > 80:
        health_score -= 20
    if system["memory_percent"] > 85:
        health_score -= 25

    return jsonify(
        {
            "status": "healthy" if health_score >= 70 else "degraded",
            "health_score": max(0, health_score),
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "agents": agents,
            "skills": skills,
        }
    )


@app.route("/api/services", methods=["GET"])
def services_status():
    """所有服务状态"""
    services = [
        {
            "name": "auth_service",
            "port": 5444,
            "url": "https://localhost:5444/auth/verify",
        },
        {
            "name": "driver_service",
            "port": 5443,
            "url": "https://localhost:5443/health",
        },
        {"name": "preference_service", "port": 5445, "url": "https://localhost:5445/"},
        {
            "name": "ollama",
            "port": 11434,
            "url": "config_loader.get_ollama_url()/api/tags",
        },
        {"name": "comfyui", "port": 8188, "url": "http://localhost:8188/"},
    ]

    results = []
    for svc in services:
        try:
            resp = requests.get(svc["url"], timeout=3, verify=False)
            results.append(
                {
                    "name": svc["name"],
                    "port": svc["port"],
                    "status": "up" if resp.status_code == 200 else "down",
                    "code": resp.status_code,
                }
            )
        except Exception as e:
            results.append(
                {
                    "name": svc["name"],
                    "port": svc["port"],
                    "status": "down",
                    "error": str(e)[:50],
                }
            )

    return jsonify({"services": results, "timestamp": datetime.now().isoformat()})


@app.route("/api/heartbeat/<agent_name>", methods=["POST"])
def heartbeat(agent_name):
    """Agent 心跳"""
    try:
        from lib.agent_watchdog import watchdog

        watchdog.heartbeat(agent_name)
    except Exception as e:
        pass
    return jsonify({"status": "ok", "agent": agent_name})


if __name__ == "__main__":
    print("=" * 50)
    print("🔒 ClawsJoy 安全 Web Dashboard")
    print("=" * 50)
    print("端口: 5446")
    print("健康检查: https://localhost:5446/api/health")
    print("服务状态: https://localhost:5446/api/services")
    print("=" * 50)
    app.run(
        host="0.0.0.0",
        port=5446,
        debug=False,
        ssl_context=("ssl/cert.pem", "ssl/key.pem"),
    )
