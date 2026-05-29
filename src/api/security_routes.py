from lib.smart_config import smart_config
"""安全监控路由"""
from flask import jsonify, request
from src.lib.security.skill_scanner import skill_scanner
from src.lib.security.community_validator import community_validator

def register_security_routes(app):
    """注册安全路由"""
    
    @app.route('/api/security/scan', methods=['POST'])
    def scan_skill():
        data = request.json
        file_path = data.get("file_path")
        if not file_path:
            return jsonify({"error": "需要提供文件路径"}), 400
        result = skill_scanner.scan_skill_file(file_path)
        return jsonify(result)
    
    @app.route('/api/security/scan/directory', methods=['POST'])
    def scan_directory():
        from pathlib import Path
        data = request.json
        directory = data.get("directory", "src/skills/atomic")
        scan_dir = Path(directory)
        results = {}
        for skill_file in scan_dir.rglob("*.py"):
            if skill_file.stem != "__init__":
                result = skill_scanner.scan_skill_file(str(skill_file))
                results[skill_file.stem] = result
        return jsonify({
            "scanned": len(results),
            "results": results,
            "report": skill_scanner.generate_report()
        })
    
    @app.route('/api/security/report', methods=['GET'])
    def security_report():
        return jsonify(skill_scanner.generate_report())
    
    @app.route('/api/community/validate', methods=['POST'])
    def validate_community_skill():
        data = request.json
        url = data.get("url")
        skill_code = data.get("code")
        if url:
            result = community_validator.validate_url(url)
        elif skill_code:
            result = community_validator.validate_skill(skill_code)
        else:
            return jsonify({"error": "需要提供 URL 或技能代码"}), 400
        return jsonify(result)
    
    print("✅ 安全路由已注册")
