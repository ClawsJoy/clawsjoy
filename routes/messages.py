import json
from pathlib import Path

from flask import Blueprint, jsonify, request

from lib.path_manager import path_manager

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/api/agents/messages", methods=["GET"])
def get_messages():
    try:
        agent = request.args.get("agent")
        limit = int(request.args.get("limit", 20))
        done_dir = path_manager.get_absolute("data.exchange.done")
        messages = []
        if done_dir.exists():
            for f in sorted(done_dir.glob("*.json"), reverse=True)[:limit]:
                try:
                    with open(f) as fp:
                        msg = json.load(fp)
                    if agent and msg.get("to") != agent and msg.get("from") != agent:
                        continue
                    messages.append(msg)
                except Exception as e:
                    pass
        return jsonify({"messages": messages, "count": len(messages)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
