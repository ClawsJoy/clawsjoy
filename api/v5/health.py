#!/usr/bin/env python3
"""Health - Health 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from flask import Blueprint, jsonify
import psutil
import time

health_bp = Blueprint('health', __name__, url_prefix='/api/v5')


@health_bp.route('/health', methods=['GET'])
def health():
    """基础健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "clawsjoy-v5",
        "version": "5.0",
        "timestamp": time.time()
    })


@health_bp.route('/ready', methods=['GET'])
def readiness():
    """就绪探针"""
    # 检查依赖服务
    dependencies = {
        "ollama": _check_ollama(),
        "storage": _check_storage()
    }
    
    all_ready = all(dependencies.values())
    status_code = 200 if all_ready else 503
    
    return jsonify({
        "ready": all_ready,
        "dependencies": dependencies
    }), status_code


@health_bp.route('/live', methods=['GET'])
def liveness():
    """存活探针"""
    return jsonify({"alive": True}), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics"""
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "connections": len(psutil.net_connections())
    })


def _check_ollama() -> bool:
    """检查 Ollama 服务"""
    import requests
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        return resp.status_code == 200
    except:
        return False


def _check_storage() -> bool:
    """检查存储"""
    from pathlib import Path
    return Path("data/v5").exists()
