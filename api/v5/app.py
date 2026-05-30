"""v5 API 主入口"""
import sys
import os
from pathlib import Path

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/v5/health', methods=['GET'])
def health():
    return jsonify({"service": "clawsjoy-v5", "status": "ok", "version": "5.0"})


@app.route('/api/v5/ready', methods=['GET'])
def ready():
    return jsonify({"ready": True})


@app.route('/api/v5/live', methods=['GET'])
def live():
    return jsonify({"alive": True})


# 延迟导入函数
def register_routes():
    try:
        from api.v5.agent import register_agent_routes
        register_agent_routes(app)
        print("   ✅ Agent 路由已注册")
    except Exception as e:
        print(f"   ❌ Agent 路由注册失败: {e}")
    
    try:
#         from .async import register_async_routes
        register_async_routes(app)
        print("   ✅ 异步路由已注册")
    except Exception as e:
        print(f"   ❌ 异步路由注册失败: {e}")


if __name__ == '__main__':
    print("🚀 ClawsJoy v5.0 启动")
    print(f"   📁 项目路径: {PROJECT_ROOT}")
    
    # 注册路由
    register_routes()
    
    print("   📡 API: http://localhost:5003/api/v5/")
    print("   💬 聊天: http://localhost:5003/api/v5/agent/chat")
    print("   ⏱️ 异步: http://localhost:5003/api/v5/async/chat")
    
    app.run(host='0.0.0.0', port=5003, debug=False)
