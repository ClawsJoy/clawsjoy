"""统一注册中心 API"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path

# 先创建 app
app = Flask(__name__)
CORS(app)

# 导入注册中心模块
from lib.service_registry_v2 import service_registry
from lib.skill_registry_v2 import skill_registry
from agents.multi.agent_registry_v2 import agent_registry

# ========== 静态页面 ==========
@app.route('/')
def registry_index():
    html_path = Path(__file__).parent / 'registry_dashboard.html'
    if html_path.exists():
        return html_path.read_text()
    return "注册中心 API 运行中"

@app.route('/dashboard')
def registry_dashboard_page():
    html_path = Path(__file__).parent / 'registry_dashboard.html'
    if html_path.exists():
        return html_path.read_text()
    return "注册中心 API 运行中"

# ========== 服务注册 API ==========
@app.route('/api/registry/services', methods=['GET'])
def get_services():
    """获取所有服务"""
    return jsonify(service_registry.get_stats())

@app.route('/api/registry/services/active', methods=['GET'])
def get_active_services():
    """获取活跃服务"""
    return jsonify({"active": service_registry.list_active()})

@app.route('/api/registry/services/<name>/health', methods=['GET'])
def service_health(name):
    """服务健康检查"""
    is_healthy = service_registry.health_check(name)
    return jsonify({"name": name, "healthy": is_healthy})

@app.route('/api/registry/services/<name>/heartbeat', methods=['POST'])
def service_heartbeat(name):
    """服务心跳"""
    result = service_registry.heartbeat(name)
    return jsonify({"name": name, "success": result})

# ========== 技能注册 API ==========
@app.route('/api/registry/skills', methods=['GET'])
def get_skills():
    """获取所有技能"""
    category = request.args.get('category')
    if category:
        skills = skill_registry.list_by_category(category)
    else:
        skills = skill_registry.list_all()
    return jsonify({"skills": skills, "total": len(skills)})

@app.route('/api/registry/skills/stats', methods=['GET'])
def get_skills_stats():
    """获取技能统计"""
    return jsonify(skill_registry.get_stats())

@app.route('/api/registry/skills/<name>', methods=['GET'])
def get_skill(name):
    """获取技能详情"""
    skill = skill_registry.get(name)
    if skill:
        return jsonify({
            "name": skill.name, 
            "version": skill.version, 
            "category": skill.category, 
            "description": skill.description,
            "dependencies": skill.dependencies, 
            "enabled": skill.enabled
        })
    return jsonify({"error": "技能不存在"}), 404

@app.route('/api/registry/skills/<name>/enable', methods=['POST'])
def enable_skill(name):
    """启用技能"""
    result = skill_registry.enable(name)
    return jsonify({"name": name, "enabled": result})

@app.route('/api/registry/skills/<name>/disable', methods=['POST'])
def disable_skill(name):
    """禁用技能"""
    result = skill_registry.disable(name)
    return jsonify({"name": name, "disabled": result})

@app.route('/api/registry/skills/<name>/reload', methods=['POST'])
def reload_skill(name):
    """热加载技能"""
    result = skill_registry.reload(name)
    return jsonify({"name": name, "reloaded": result})

# ========== Agent 注册 API ==========
@app.route('/api/registry/agents', methods=['GET'])
def get_agents():
    """获取所有 Agent"""
    return jsonify(agent_registry.get_stats())

@app.route('/api/registry/agents/capability/<capability>', methods=['GET'])
def find_agents_by_capability(capability):
    """根据能力查找 Agent"""
    agents = agent_registry.find_by_capability(capability)
    return jsonify({"capability": capability, "agents": [a.name for a in agents]})

@app.route('/api/registry/agents/route', methods=['POST'])
def route_request():
    """路由请求"""
    data = request.json
    capability = data.get('capability')
    agent = agent_registry.route_request(capability)
    return jsonify({"capability": capability, "routed_to": agent})

# ========== 统一仪表板 ==========
@app.route('/api/registry/dashboard', methods=['GET'])
def registry_dashboard():
    """注册中心仪表板"""
    return jsonify({
        "services": service_registry.get_stats(),
        "skills": skill_registry.get_stats(),
        "agents": agent_registry.get_stats(),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

# ========== 启动服务 ==========
if __name__ == '__main__':
    port = 5022
    print(f"📋 统一注册中心 API 启动: http://localhost:{port}")
    print("   /api/registry/services - 服务列表")
    print("   /api/registry/skills - 技能列表")
    print("   /api/registry/agents - Agent 列表")
    print("   /api/registry/dashboard - 仪表板")
    app.run(host='0.0.0.0', port=port, debug=False)
