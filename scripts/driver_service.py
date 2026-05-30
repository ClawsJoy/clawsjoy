#!/usr/bin/env python3
#!/usr/bin/env python3
"""Driver Service - Driver Service 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path
import yaml

# 先创建 app
app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "driver_service"})


@app.route('/api/driver/config/desensitization', methods=['GET'])
def get_desensitization_config():
    config_file = Path("config/driver/desensitization.yaml")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    return jsonify({"error": "Config not found"}), 404


@app.route('/api/driver/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "version": "1.0.0",
        "hash": "test123",
        "drivers": []
    })


@app.route('/api/driver/hash', methods=['GET'])
def get_hash():
    return jsonify({"hash": "test123"})


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 ClawsJoy 驱动服务")
    print("=" * 50)
    print("端口: 5013")
    print("健康检查: http://localhost:5013/health")
    print("脱敏配置: http://localhost:5013/api/driver/config/desensitization")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5013, debug=False)
