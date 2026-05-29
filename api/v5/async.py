"""异步任务 API"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Blueprint, request, jsonify
import threading
import uuid
import time

async_bp = Blueprint('async', __name__, url_prefix='/api/v5/async')
tasks = {}


def register_async_routes(app):
    """注册异步路由"""
    
    @async_bp.route('/chat', methods=['POST'])
    def async_chat():
        from core.v5.agent.orchestrator.main_agent import MainAgent
        
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "message required"}), 400
        
        task_id = str(uuid.uuid4())[:8]
        
        def process():
            agent = MainAgent(user_id)
            result = agent.process(message)
            tasks[task_id] = {"status": "completed", "result": result, "completed_at": time.time()}
        
        tasks[task_id] = {"status": "pending", "created_at": time.time()}
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
        
        return jsonify({"task_id": task_id, "status": "pending"})
    
    @async_bp.route('/result/<task_id>', methods=['GET'])
    def get_result(task_id):
        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        if task["status"] == "completed":
            return jsonify(task["result"])
        return jsonify({"status": "pending", "task_id": task_id})
    
    app.register_blueprint(async_bp)
    print("   ✅ 异步路由已注册")
