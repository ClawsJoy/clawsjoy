#!/usr/bin/env python3
"""Health API - 健康检查接口"""

from flask import Blueprint, jsonify

api_bp = Blueprint("v5_health", __name__, url_prefix="/api/v5")


@api_bp.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify(
        {"status": "healthy", "service": "clawsjoy-gateway", "version": "5.0.0"}
    )


@api_bp.route("/ready", methods=["GET"])
def ready():
    """就绪检查"""
    return jsonify({"status": "ready"})


@api_bp.route("/live", methods=["GET"])
def live():
    """存活检查"""
    return jsonify({"status": "alive"})
