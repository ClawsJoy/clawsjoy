"""Agent API"""
from flask import Blueprint, request, jsonify
from core.v5.agent.decision import DecisionAgent
from core.v5.agent.chat import ChatAgent
from core.v5.agent.code import CodeAgent

api_bp = Blueprint('v5_agents', __name__, url_prefix='/api/v5')


@api_bp.route('/decision', methods=['POST'])
def decision():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    agent = DecisionAgent(user_id)
    result = agent.process(message)
    return jsonify(result)


@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    agent = ChatAgent(user_id)
    result = agent.process(message)
    return jsonify(result)


@api_bp.route('/code', methods=['POST'])
def code():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    agent = CodeAgent(user_id)
    result = agent.process(message)
    return jsonify(result)


def register(app):
    app.register_blueprint(api_bp)
