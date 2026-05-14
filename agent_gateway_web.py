#!/usr/bin/env python3
"""ClawsJoy 主网关 - 使用配置中心和技能加载器"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

# 导入配置中心
from lib.config import config
from lib.service_registry import service_registry
from lib.skill_loader import skill_loader

app = Flask(__name__)
CORS(app)

# ========== 健康检查 ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "service": "gateway",
        "status": "ok",
        "version": "3.0",
        "config_loaded": True
    })

# ========== 配置信息 ==========
@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置（不包含敏感信息）"""
    return jsonify({
        "services": config.get("services"),
        "llm": {
            "endpoint": config.get("llm.endpoint"),
            "default_model": config.get("llm.default_model")
        },
        "skills_count": len(skill_loader.list_skills())
    })

# ========== 技能相关 API ==========
@app.route('/api/skills', methods=['GET'])
def list_skills():
    """列出所有已声明的技能"""
    return jsonify({
        "skills": skill_loader.list_skills(),
        "total": len(skill_loader.list_skills())
    })

@app.route('/api/skills/<name>', methods=['GET'])
def get_skill(name):
    """获取技能详情"""
    info = skill_loader.get_skill_info(name)
    if info:
        return jsonify(info)
    return jsonify({"error": "技能不存在"}), 404

@app.route('/api/skills/execute', methods=['POST'])
def execute_skill():
    """执行技能"""
    data = request.json
    skill_name = data.get('skill')
    params = data.get('params', {})
    
    if not skill_name:
        return jsonify({"error": "缺少技能名"}), 400
    
    result = skill_loader.execute_skill(skill_name, params)
    return jsonify(result)

# ========== 大脑调度 API ==========
@app.route('/api/agent/v3/do_anything', methods=['POST'])
def do_anything():
    """大脑自主决策执行"""
    data = request.json
    goal = data.get('goal', '')
    
    if not goal:
        return jsonify({"error": "需要提供目标"}), 400
    
    try:
        from skills.do_anything import skill
        result = skill.execute({"goal": goal})
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ========== 服务注册 API ==========
@app.route('/api/services', methods=['GET'])
def list_services():
    """列出所有已注册服务"""
    return jsonify({
        "services": service_registry.list_all(),
        "details": service_registry.services
    })

@app.route('/api/services/<name>/health', methods=['GET'])
def service_health(name):
    """检查服务健康状态"""
    is_healthy = service_registry.health_check(name)
    return jsonify({"service": name, "healthy": is_healthy})

# ========== 旧版 API 兼容 ==========
@app.route('/api/agent/v3/code_assistant/chat', methods=['POST'])
def code_assistant():
    """代码助手兼容接口"""
    data = request.json
    message = data.get('message', '')
    
    try:
        from skills.do_anything import skill
        result = skill.execute({"goal": message})
        return jsonify({"response": str(result.get('results', []))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/brain/v2/stats', methods=['GET'])
def brain_stats():
    """大脑统计信息"""
    try:
        from agent_core.brain_enhanced import brain
        stats = brain.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== 文件操作 API ==========
@app.route('/api/file/list', methods=['GET'])
def list_files():
    """列出上传的文件"""
    from pathlib import Path
    upload_dir = Path("data/uploads")
    if upload_dir.exists():
        files = [f.name for f in upload_dir.iterdir() if f.is_file()]
        return jsonify({"files": files, "count": len(files)})
    return jsonify({"files": [], "count": 0})

# ========== 启动服务 ==========
if __name__ == '__main__':
    # 从配置获取端口
    port = config.get('services.gateway.port', 5002)
    host = config.get('services.gateway.host', '0.0.0.0')
    
    # 注册自身到服务注册中心
    service_registry.register('gateway', port, host)
    
    print("=" * 50)
    print("🧠 ClawsJoy 网关启动")
    print("=" * 50)
    print(f"📍 访问: http://localhost:{port}")
    print(f"📋 已声明技能: {len(skill_loader.list_skills())}")
    print(f"🔧 配置中心: {'✅' if config.get('services.gateway.port') else '❌'}")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=False)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空响应，不记录404

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空响应，不记录404
