"""技能市场 API"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from lib.skill_market import skill_market
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/api/market/skills', methods=['GET'])
def list_market_skills():
    local = skill_market.list_local()
    return jsonify({"skills": local, "total": len(local)})

@app.route('/api/market/skills', methods=['POST'])
def publish_skill():
    data = request.json
    result = skill_market.publish(
        data.get('name'),
        data.get('author', 'anonymous'),
        data.get('description', ''),
        data.get('version', '1.0.0')
    )
    return jsonify(result)

@app.route('/api/market/skills/<name>/download', methods=['GET'])
def download_skill(name):
    skill_path = Path(f"skills/{name}.py")
    if skill_path.exists():
        return send_file(skill_path, as_attachment=True)
    return jsonify({"error": "技能不存在"}), 404

@app.route('/api/market/install', methods=['POST'])
def install_skill():
    data = request.json
    result = skill_market.install(data.get('name'), data.get('source_url'))
    return jsonify(result)

if __name__ == '__main__':
    print("🏪 技能市场 API 启动: http://localhost:5024")
    app.run(host='0.0.0.0', port=5024, debug=False)
