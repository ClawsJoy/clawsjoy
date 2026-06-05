#!/usr/bin/env python3
"""memory API"""

from flask import Blueprint, jsonify, request

api_bp = Blueprint("v5_memory", __name__, url_prefix="/api/v5")


@api_bp.route("/memory", methods=["POST"])
def handle():
    data = request.get_json() or {}
    return jsonify({"success": True, "message": data.get("message", "")})
