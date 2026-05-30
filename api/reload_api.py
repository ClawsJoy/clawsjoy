#!/usr/bin/env python3
"""Reload Api - Reload Api 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from flask import Blueprint, jsonify
from lib.route_registry import route_registry
from lib.config_auto_watcher import config_auto_watcher

reload_bp = Blueprint('reload', __name__, url_prefix='/api/reload')

@reload_bp.route('/routes', methods=['POST'])
def reload_routes():
    """热重载路由"""
    try:
        route_registry.reload()
        return jsonify({
            "success": True,
            "message": "路由已重载",
            "routes_count": len(route_registry._routes)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@reload_bp.route('/config', methods=['POST'])
def reload_config():
    """热重载配置"""
    try:
        config_auto_watcher.trigger_reload()
        return jsonify({"success": True, "message": "配置重载已触发"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def register_reload_api(app):
    app.register_blueprint(reload_bp)
    print("   ✅ 热重载 API 已注册")
