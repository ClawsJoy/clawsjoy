#!/usr/bin/env python3
#!/usr/bin/env python3
"""Driver Service Https - Driver Service Https 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path
import yaml

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "driver_service", "secure": True})


@app.route('/api/driver/config/desensitization', methods=['GET'])
def get_desensitization_config():
    config_file = Path("config/driver/desensitization.yaml")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    return jsonify({"error": "Config not found"}), 404


if __name__ == '__main__':
    print("=" * 50)
    print("🔒 ClawsJoy HTTPS 驱动服务")
    print("=" * 50)
    print("端口: 5443")
    print("健康检查: https://localhost:5443/health")
    print("=" * 50)
    
    # 使用 Flask 内置 SSL
    app.run(host='0.0.0.0', port=5443, debug=False, 
            ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
