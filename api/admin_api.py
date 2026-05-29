"""管理员 API - 统一管理接口"""

from flask import Blueprint, request, jsonify
from core.agents.agent_manager import agent_manager
from lib.skill_adapter import unified_skill_interface
from lib.config_auto_watcher import config_auto_watcher

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/agents', methods=['GET'])
def list_agents():
    """列出所有 Agent"""
    return jsonify({
        "success": True,
        "agents": agent_manager.list_agents(),
        "total": len(agent_manager.list_agents())
    })

@admin_bp.route('/agents/<agent_name>', methods=['GET'])
def get_agent(agent_name):
    """获取 Agent 详情"""
    agent = agent_manager.get_agent(agent_name)
    if not agent:
        return jsonify({"success": False, "error": "Agent not found"}), 404
    return jsonify({"success": True, "agent": agent})

@admin_bp.route('/agents/<agent_name>', methods=['PUT'])
def update_agent(agent_name):
    """更新 Agent"""
    data = request.get_json() or {}
    if agent_name not in agent_manager.agents:
        return jsonify({"success": False, "error": "Agent not found"}), 404
    agent_manager.agents[agent_name].update(data)
    agent_manager._save()
    return jsonify({"success": True, "message": f"Agent {agent_name} 已更新"})

@admin_bp.route('/agents/<agent_name>/toggle', methods=['POST'])
def toggle_agent(agent_name):
    """启用/禁用 Agent"""
    data = request.get_json() or {}
    enabled = data.get('enabled', True)
    if agent_name not in agent_manager.agents:
        return jsonify({"success": False, "error": "Agent not found"}), 404
    agent_manager.agents[agent_name]['enabled'] = enabled
    agent_manager._save()
    return jsonify({"success": True, "enabled": enabled})

@admin_bp.route('/reload', methods=['POST'])
def reload_config():
    """热重载配置"""
    config_auto_watcher.trigger_reload()
    return jsonify({"success": True, "message": "配置已热重载"})

@admin_bp.route('/skills', methods=['GET'])
def list_skills():
    """列出所有技能"""
    skills = unified_skill_interface.list_all()
    return jsonify({
        "success": True,
        "skills": skills,
        "total": len(skills)
    })

def register_admin_api(app):
    app.register_blueprint(admin_bp)
    print("   ✅ 管理员 API 已注册")
