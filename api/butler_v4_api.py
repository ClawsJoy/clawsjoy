"""私人管家 v4.0 API 适配器"""
from flask import Blueprint, request, jsonify
from core.butler.butler_v4 import create_butler

butler_v4_bp = Blueprint('butler_v4', __name__, url_prefix='/api/butler/v4')


@butler_v4_bp.route('/chat', methods=['POST'])
def chat():
    """对话接口"""
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"success": False, "error": "message required"}), 400
    
    butler = create_butler(user_id)
    result = butler.process(message)
    
    return jsonify(result)


@butler_v4_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    user_id = request.args.get('user_id', 'default')
    butler = create_butler(user_id)
    return jsonify(butler.get_stats())


# 同时保持旧接口兼容
def register_butler_routes(app):
    """注册管家路由（兼容旧接口）"""
    
    @app.route('/api/butler/chat', methods=['POST'])
    def butler_chat_compat():
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "消息为空", "success": False}), 400
        
        butler = create_butler(user_id)
        result = butler.process(message)
        return jsonify({
            "response": result.get('response', ''),
            "success": result.get('success', True),
            "user_id": user_id
        })
    
    @app.route('/api/butler/rename', methods=['POST'])
    def butler_rename_compat():
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        new_name = data.get('name', '')
        
        butler = create_butler(user_id)
        result = butler.process(f"叫我{new_name}")
        
        return jsonify({
            "response": result.get('response', ''),
            "success": result.get('success', True),
            "new_name": new_name,
            "user_id": user_id
        })
    
    @app.route('/api/butler/todo', methods=['POST', 'GET'])
    def butler_todo_compat():
        user_id = request.args.get('user_id') or request.get_json().get('user_id') if request.get_json() else 'default'
        butler = create_butler(user_id)
        
        if request.method == 'POST':
            data = request.get_json() or {}
            task = data.get('task', '')
            if task:
                result = butler.process(f"记住{task}")
                return jsonify({
                    "success": True,
                    "message": "已添加待办",
                    "todos": butler.memory.recall_preference("todos") or []
                })
        
        todos = butler.memory.recall_preference("todos") or []
        return jsonify({"success": True, "todos": todos, "user_id": user_id})
    
    print("   ✅ 私人管家 v4.0 API 已注册")
