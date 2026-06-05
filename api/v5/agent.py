#!/usr/bin/env python3
"""Agent - Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Blueprint, jsonify, request

agent_bp = Blueprint("agent", __name__, url_prefix="/api/v5/agent")


def register_agent_routes(app):
    """注册 Agent 路由"""

    @agent_bp.route("/chat", methods=["POST"])
    def chat():
        from core.v5.agent.orchestrator.main_agent import MainAgent

        data = request.get_json() or {}
        user_id = data.get("user_id", "default")
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "message required"}), 400

        agent = MainAgent(user_id)
        result = agent.process(message)
        return jsonify(result)

    @agent_bp.route("/status", methods=["GET"])
    def status():
        from core.v5.agent.orchestrator.main_agent import MainAgent

        user_id = request.args.get("user_id", "default")
        agent = MainAgent(user_id)
        return jsonify(
            {"success": True, "status": agent.get_state(), "user_id": user_id}
        )

    app.register_blueprint(agent_bp)
    print("   ✅ Agent 路由已注册")
