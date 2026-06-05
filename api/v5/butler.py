#!/usr/bin/env python3
"""Butler API - 管家接口"""

from flask import Blueprint, jsonify, request

from core.butler.butler_v4 import create_butler

api_bp = Blueprint("v5_butler", __name__, url_prefix="/api/v5/butler")


@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default")
    message = data.get("message", "")
    butler = create_butler(user_id)
    result = (
        butler.process(message)
        if hasattr(butler, "process")
        else {"response": f"收到: {message}"}
    )
    return jsonify({"success": True, "response": result.get("response", "")})


@api_bp.route("/todo", methods=["POST", "GET"])
def todo():
    user_id = request.args.get("user_id", "default")
    butler = create_butler(user_id)
    if request.method == "POST":
        data = request.get_json() or {}
        task = data.get("task", "")
        if hasattr(butler, "add_todo"):
            butler.add_todo(task)
        return jsonify({"success": True, "message": f"已添加待办: {task}"})
    else:
        todos = butler.get_todos() if hasattr(butler, "get_todos") else []
        return jsonify({"success": True, "todos": todos})
