"""私人管家 v5.0 API"""
from flask import Blueprint, request, jsonify
from core.v5.agent.butler import create_butler

butler_v5_bp = Blueprint('butler_v5', __name__, url_prefix='/api/v5/butler')


@butler_v5_bp.route('/chat', methods=['POST'])
def chat():
    """对话"""
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    butler = create_butler(user_id)
    result = butler.process(message)
    
    return jsonify(result)


@butler_v5_bp.route('/state', methods=['GET'])
def get_state():
    """获取状态"""
    user_id = request.args.get('user_id', 'default')
    butler = create_butler(user_id)
    return jsonify(butler.get_full_state())


@butler_v5_bp.route('/rename', methods=['POST'])
def rename():
    """改名"""
    data = request.get_json() or {}
    user_id = data.get('user_id', 'default')
    new_name = data.get('name', '')
    
    butler = create_butler(user_id)
    result = butler.process(f"叫我{new_name}")
    
    return jsonify(result)


@butler_v5_bp.route('/todo', methods=['GET', 'POST'])
def todo():
    """待办管理"""
    user_id = None
    
    if request.method == 'GET':
        user_id = request.args.get('user_id', 'default')
        butler = create_butler(user_id)
        result = butler.process("查看待办")
    else:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        task = data.get('task', '')
        butler = create_butler(user_id)
        result = butler.process(f"记住{task}")
    
    return jsonify(result)


def register_v5_routes(app):
    """注册 v5 路由"""
    app.register_blueprint(butler_v5_bp)
    
    # 同时保持旧路由兼容
    @app.route('/api/butler/chat', methods=['POST'])
    def butler_chat_v5_compat():
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        butler = create_butler(user_id)
        result = butler.process(message)
        return jsonify({
            "response": result.get('response', ''),
            "success": True,
            "user_id": user_id
        })
    
    @app.route('/api/butler/rename', methods=['POST'])
    def butler_rename_v5_compat():
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        new_name = data.get('name', '')
        butler = create_butler(user_id)
        result = butler.process(f"叫我{new_name}")
        return jsonify({
            "response": result.get('response', ''),
            "success": True,
            "new_name": new_name,
            "user_id": user_id
        })
    
    @app.route('/api/butler/todo', methods=['POST', 'GET'])
    def butler_todo_v5_compat():
        user_id = request.args.get('user_id') or request.get_json().get('user_id') if request.get_json() else 'default'
        butler = create_butler(user_id)
        
        if request.method == 'POST':
            data = request.get_json() or {}
            task = data.get('task', '')
            if task:
                result = butler.process(f"记住{task}")
                todos = butler.recall("todos") or []
                return jsonify({"success": True, "todos": todos})
        
        result = butler.process("查看待办")
        return jsonify({"success": True, "todos": butler.recall("todos") or []})
    
    print("   ✅ v5.0 API 已注册")
