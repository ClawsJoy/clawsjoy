"""文件服务技能 - 让大脑能调用文件处理能力"""

from skills.skill_interface import BaseSkill
import requests

class FileServiceSkill(BaseSkill):
    name = "file_service"
    description = "文件处理服务（上传、列表、读取）"
    version = "1.0.0"
    category = "utility"
    
    def execute(self, params):
        action = params.get("action", "")
        base_url = "http://localhost:5003"
        
        if action == "list":
            resp = requests.get(f"{base_url}/files")
            return resp.json()
        elif action == "upload":
            # 需要先有文件路径
            return {"error": "请使用文件上传接口"}
        elif action == "read":
            filename = params.get("filename", "")
            resp = requests.get(f"{base_url}/read/{filename}")
            return resp.json()
        else:
            return {"error": f"Unknown action: {action}"}

skill = FileServiceSkill()
