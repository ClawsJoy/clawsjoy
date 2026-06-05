#!/usr/bin/env python3
"""chat API"""

from flask import Blueprint, jsonify, request

api_bp = Blueprint("v5_chat", __name__, url_prefix="/api/v5")


@api_bp.route("/chat", methods=["POST"])
def handle():
    data = request.get_json() or {}
    return jsonify({"success": True, "message": data.get("message", "")})
