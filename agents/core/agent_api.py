from lib.unified_config import config
"""Agent API - 核心接口"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from agents.core.core.tenant_agent import get_agent
from agents.core.core.security_agent import verify_token
from agents.core.core.memory_manager import get_memory

# 简化版本
def create_app():
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=config.get_port("gateway"))
