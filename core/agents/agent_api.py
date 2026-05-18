"""Agent API - 统一调用接口"""
from flask import Flask, jsonify, request
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from agents.agent_manager import AgentManager

app = Flask(__name__)
manager = AgentManager()

@app.route('/agents', methods=['GET'])
def list_agents():
    return jsonify({
        "agents": manager.list_agents(),
        "stats": manager.get_stats()
    })

@app.route('/agents/<name>', methods=['GET'])
def get_agent(name):
    agent = manager.get_agent(name)
    if agent:
        return jsonify({
            "name": name,
            "type": agent["type"],
            "config": agent.get("config", {}),
            "memory_stats": {
                "conversations": len(agent.get("memory", {}).get("conversations", []))
            }
        })
    return jsonify({"error": "Agent not found"}), 404

if __name__ == "__main__":
    app.run(port=5010)
