#!/usr/bin/env python3
"""Agents - Agents 模块"""

from flask import Blueprint, jsonify, request

from agents.chat_agent.agent_v4 import ChatAgentV4 as ChatAgent
from agents.code_agent.agent_v4 import CodeAgentV4 as CodeAgent
from agents.decision_agent.agent_v4 import DecisionAgentV4 as DecisionAgent

api_bp = Blueprint("v5_agents", __name__, url_prefix="/api/v5")


@api_bp.route("/decision", methods=["POST"])
def decision():
    data = request.get_json() or {}
    agent = DecisionAgent(data.get("user_id", "default"))
    result = agent.process(data.get("message", ""))
    return jsonify(result)
