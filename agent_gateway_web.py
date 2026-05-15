#!/usr/bin/env python3
"""ClawsJoy 主网关 - 完整版"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# 导入配置
from lib.config import config
from lib.service_registry import service_registry
from lib.skill_loader_v3 import skill_loader

# ========== 健康检查 ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"service": "gateway", "status": "ok", "version": "3.0"})

# ========== 技能相关 ==========
@app.route('/api/skills', methods=['GET'])
def list_skills():
    return jsonify({"skills": skill_loader.list_skills(), "total": len(skill_loader.list_skills())})

@app.route('/api/skills/execute', methods=['POST'])
def execute_skill():
    data = request.json
    skill_name = data.get('skill')
    params = data.get('params', {})
    result = skill_loader.execute(skill_name, params)
    return jsonify(result)

# ========== 大脑调度 ==========
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

# ========== 服务注册 ==========
@app.route('/api/services', methods=['GET'])
def list_services():
    return jsonify({"services": service_registry.list_all()})

# ========== Prometheus 监控 ==========
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus 监控指标"""
    try:
        from prometheus_client import generate_latest
        return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}
    except ImportError:
        return "# prometheus_client not installed\n", 200, {'Content-Type': 'text/plain'}

# ========== Swagger API 文档 ==========
@app.route('/apidocs/', methods=['GET'])
def apidocs():
    """Swagger UI"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClawsJoy API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/favicon-32x32.png">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: '#swagger-ui',
                    presets: [SwaggerUIBundle.presets.apis],
                    layout: "BaseLayout"
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/openapi.json', methods=['GET'])
def openapi():
    """OpenAPI 规范"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "ClawsJoy API", "version": "3.0.0"},
        "paths": {
            "/api/health": {"get": {"summary": "健康检查"}},
            "/api/skills": {"get": {"summary": "技能列表"}},
            "/api/agent/v3/do_anything": {"post": {"summary": "大脑调度"}},
            "/metrics": {"get": {"summary": "Prometheus 监控指标"}}
        }
    })

# ========== favicon ==========
@app.route('/favicon.ico')
def favicon():
    return '', 204

# ========== 启动 ==========
if __name__ == '__main__':
    port = 5002
    print("=" * 50)
    print("🧠 ClawsJoy 网关启动")
    print("=" * 50)
    print(f"📍 访问: http://localhost:{port}")
    print(f"📍 API 文档: http://localhost:{port}/apidocs/")
    print(f"📍 Metrics: http://localhost:{port}/metrics")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)
