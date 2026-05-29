"""数据源管理API - 分析师/决策Agent数据权限"""
from flask import Blueprint, request, jsonify
import yaml
from pathlib import Path
from datetime import datetime

datasource_bp = Blueprint('datasource', __name__, url_prefix='/api/datasource')

# 加载配置
def load_datasource_config():
    config_file = Path("config/datasource/data_sources.yaml")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    return {}

@datasource_bp.route('/sources', methods=['GET'])
def list_sources():
    """列出所有数据源（按权限过滤）"""
    role = request.args.get('role', 'user')
    config = load_datasource_config()
    
    # 根据角色过滤
    permission_levels = {
        'user': 0,
        'agent': 1,
        'analyst': 2,
        'decision': 3,
        'executor': 4,
        'admin': 5
    }
    user_level = permission_levels.get(role, 0)
    
    filtered_sources = {}
    for level, sources in config.get('data_sources', {}).items():
        level_value = permission_levels.get(level, 0)
        if level_value <= user_level:
            filtered_sources[level] = sources
    
    return jsonify({
        "success": True,
        "role": role,
        "level": user_level,
        "sources": filtered_sources
    })

@datasource_bp.route('/query', methods=['POST'])
def query_data():
    """查询数据（受权限控制）"""
    data = request.get_json() or {}
    source_id = data.get('source_id')
    role = data.get('role', 'user')
    query_params = data.get('params', {})
    
    # 权限验证
    config = load_datasource_config()
    permission_levels = {'user':0, 'agent':1, 'analyst':2, 'decision':3, 'executor':4, 'admin':5}
    
    # 查找数据源权限
    source_permission = 'user'
    for level, sources in config.get('data_sources', {}).items():
        for s in sources:
            if s.get('id') == source_id:
                source_permission = s.get('permission', 'user')
                break
    
    if permission_levels.get(role, 0) < permission_levels.get(source_permission, 0):
        return jsonify({
            "success": False,
            "error": f"权限不足: {role} 无法访问 {source_permission} 级数据源"
        }), 403
    
    # 模拟数据查询
    return jsonify({
        "success": True,
        "source_id": source_id,
        "role": role,
        "data": {
            "timestamp": datetime.now().isoformat(),
            "sample": f"查询 {source_id} 的数据结果",
            "query_params": query_params
        }
    })

@datasource_bp.route('/permissions', methods=['GET'])
def get_permissions():
    """获取权限层级"""
    config = load_datasource_config()
    return jsonify({
        "success": True,
        "hierarchy": config.get('permission_hierarchy', {}),
        "access_control": config.get('access_control', {})
    })
