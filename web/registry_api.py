"""统一注册中心 API"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

from lib.service_registry_v2 import service_registry
from lib.skill_registry_v2 import skill_registry
from lib.skill_loader_v3 import skill_loader
from agents.multi.agent_registry_v2 import agent_registry

# 静态页面
@app.route('/')
def index():
    html_path = Path(__file__).parent / 'registry_dashboard.html'
    if html_path.exists():
        return html_path.read_text()
    return "<h1>ClawsJoy 注册中心</h1>"

@app.route('/dashboard')
def dashboard():
    return index()

# 服务 API
@app.route('/api/registry/services', methods=['GET'])
def get_services():
    return jsonify(service_registry.get_stats())

@app.route('/api/registry/services/<name>/health', methods=['GET'])
def service_health(name):
    is_healthy = service_registry.health_check(name)
    return jsonify({"name": name, "healthy": is_healthy})

# 技能 API - 返回所有技能
@app.route('/api/registry/skills', methods=['GET'])
def get_skills():
    """获取所有技能列表"""
    skills = skill_loader.list_skills()
    return jsonify({"skills": skills, "total": len(skills)})

@app.route('/api/registry/skills/stats', methods=['GET'])
def get_skills_stats():
    """获取技能统计"""
    categories = {}
    for skill_name in skill_loader.list_skills():
        # 简单分类
        if skill_name in ['add', 'multiply', 'divide', 'math_enhanced']:
            cat = 'math'
        elif skill_name in ['remove_bg', 'spider', 'image_slideshow']:
            cat = 'image'
        elif skill_name in ['manju_maker', 'video_uploader', 'add_subtitles']:
            cat = 'video'
        elif skill_name in ['do_anything', 'calibrated_executor', 'quality_gate']:
            cat = 'core'
        elif skill_name in ['text_processor', 'json_parser', 'hot_dual_script']:
            cat = 'text'
        else:
            cat = 'other'
        categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({
        "total": len(skill_loader.list_skills()),
        "by_category": categories
    })

@app.route('/api/registry/skills/<name>/execute', methods=['POST'])
def execute_skill(name):
    params = request.json or {}
    result = skill_loader.execute(name, params)
    return jsonify(result)

# Agent API
@app.route('/api/registry/agents', methods=['GET'])
def get_agents():
    return jsonify(agent_registry.get_stats())

@app.route('/api/registry/agents/route', methods=['POST'])
def route_request():
    data = request.json
    capability = data.get('capability')
    agent = agent_registry.route_request(capability)
    return jsonify({"capability": capability, "routed_to": agent})

# 仪表板 API
@app.route('/api/registry/dashboard', methods=['GET'])
def registry_dashboard():
    return jsonify({
        "services": service_registry.get_stats(),
        "skills": {
            "total": len(skill_loader.list_skills()),
            "by_category": skill_loader.get_categories()
        },
        "agents": agent_registry.get_stats(),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 5022
    print(f"📋 统一注册中心 API 启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
