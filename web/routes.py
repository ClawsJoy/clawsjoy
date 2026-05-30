"""Web 路由"""

from flask import Blueprint, send_from_directory, render_template_string
from pathlib import Path

web_bp = Blueprint('web', __name__, url_prefix='')

@web_bp.route('/mobile/')
def mobile():
    """移动端页面"""
    index_path = Path(__file__).parent / 'mobile' / 'index.html'
    if index_path.exists():
        return send_from_directory(Path(__file__).parent, 'mobile/index.html')
    return "移动端页面开发中", 404

@web_bp.route('/mobile/<path:filename>')
def mobile_static(filename):
    """移动端静态文件"""
    return send_from_directory(Path(__file__).parent / 'mobile', filename)
