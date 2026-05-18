from lib.smart_config import smart_config
#!/usr/bin/env python3
"""Registry Center - 简化版"""
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
@app.route('/api/registry/dashboard')
def health():
    return jsonify({"status": "ok", "service": "registry-center"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5022)
