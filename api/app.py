#!/usr/bin/env python3
#!/usr/bin/env python3
"""App - App 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify
from web.api_v4 import api_bp
from intelligence.service_v4 import intelligence_service

app = Flask(__name__)
app.register_blueprint(api_bp)


@app.route('/')
def index():
    return jsonify({
        "name": "ClawsJoy",
        "version": "4.0.0",
        "status": "running",
        "intelligence": intelligence_service.get_status()
    })


@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "4.0.0"})


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ClawsJoy 4.0.0 智能系统")
    print("=" * 50)
    print(f"智能服务: v{intelligence_service.VERSION}")
    print(f"API 地址: http://0.0.0.0:5011")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5011, debug=False)
