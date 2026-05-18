#!/usr/bin/env python3
"""ClawsJoy 主网关 - 完整版"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, request
from flask_cors import CORS
from lib.smart_config import smart_config
from lib.skill_loader_v3 import skill_loader

app = Flask(__name__)
CORS(app)

# ========== 基础 API ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"service": "gateway", "status": "ok", "version": "3.0"})

@app.route('/api/skills', methods=['GET'])
def list_skills():
    skills = skill_loader.list_skills()
    return jsonify({"skills": skills, "total": len(skills)})

@app.route('/api/skills/execute', methods=['POST'])
def execute_skill():
    data = request.json
    skill_name = data.get('skill')
    params = data.get('params', {})
    result = skill_loader.execute(skill_name, params)
    return jsonify(result)

@app.route('/api/agent/v3/do_anything', methods=['POST'])
def do_anything():
    data = request.json
    goal = data.get('goal', '')
    if not goal:
        return jsonify({"error": "需要提供目标"}), 400
    try:
        from skills.core.do_anything import skill
        result = skill.execute({"goal": goal})
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ========== Agent API ==========
@app.route('/api/agents/list', methods=['GET'])
def list_agents():
    try:
        from lib.agent_registry import agent_registry
        return jsonify({
            "agents": agent_registry.list_all(),
            "stats": agent_registry.get_stats()
        })
    except Exception as e:
        return jsonify({"error": str(e), "agents": []})

@app.route('/api/agents/health', methods=['GET'])
def agents_health():
    try:
        from lib.agent_health import agent_health
        return jsonify(agent_health.get_summary())
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/agents/info', methods=['GET'])
def agents_info():
    try:
        from agents.agent_manager import agent_manager
        return jsonify({
            "agents": agent_manager.list_agents(),
            "stats": agent_manager.get_stats()
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ========== 日志 API ==========
@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        service = request.args.get('service')
        lines = int(request.args.get('lines', 50))
        from lib.log_aggregator import log_aggregator
        logs = log_aggregator.get_logs(service, lines)
        return jsonify({"logs": logs, "summary": log_aggregator.get_summary()})
    except Exception as e:
        return jsonify({"error": str(e), "logs": {}})

@app.route('/api/logs/search', methods=['GET'])
def search_logs():
    try:
        keyword = request.args.get('q', '')
        service = request.args.get('service')
        lines = int(request.args.get('lines', 20))
        from lib.log_aggregator import log_aggregator
        results = log_aggregator.search_logs(keyword, service, lines)
        return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e), "results": []})

@app.route('/api/logs/errors', methods=['GET'])
def get_errors():
    try:
        service = request.args.get('service')
        lines = int(request.args.get('lines', 20))
        from lib.log_aggregator import log_aggregator
        errors = log_aggregator.get_errors(service, lines)
        return jsonify({"errors": errors, "count": len(errors)})
    except Exception as e:
        return jsonify({"error": str(e), "errors": []})

# ========== Agent 通信 API ==========
@app.route('/api/agents/messages', methods=['GET'])
def get_agent_messages():
    try:
        agent_id = request.args.get('agent')
        from lib.agent_communication import agent_comm
        messages = agent_comm.get_messages(agent_id)
        return jsonify({"messages": messages, "count": len(messages)})
    except Exception as e:
        return jsonify({"error": str(e), "messages": []})

@app.route('/api/agents/send', methods=['POST'])
def send_agent_message():
    try:
        data = request.json
        from_agent = data.get('from')
        to_agent = data.get('to')
        message = data.get('message')
        from lib.agent_communication import agent_comm
        result = agent_comm.send_message(from_agent, to_agent, message)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ========== 服务 API ==========
@app.route('/api/services', methods=['GET'])
def list_services():
    try:
        from lib.service_registry import service_registry
        return jsonify({"services": service_registry.services})
    except Exception as e:
        return jsonify({"error": str(e), "services": {}})

# ========== 监控指标 ==========
@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        from prometheus_client import generate_latest
        return generate_latest(), 200, {'Content-Type': 'text/plain'}
    except ImportError:
        return "# Prometheus client not installed\n", 200

if __name__ == '__main__':
    port = smart_config.get_port('gateway')
    host = smart_config.HOST
    print(f"🧠 ClawsJoy 网关启动: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "ClawsJoy Gateway",
        "version": "3.0",
        "endpoints": {
            "health": "/api/health",
            "skills": "/api/skills",
            "agents": "/api/agents/list",
            "docs": "/apidocs/"
        }
    })
