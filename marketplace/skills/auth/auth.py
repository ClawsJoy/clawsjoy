"""Auth 技能 - 标准格式"""

from typing import Dict
from skills.skill_interface import BaseSkill
import os
import requests

class AuthSkill(BaseSkill):
    name = "auth"
    description = "认证和授权管理"
    version = "1.0.0"
    category = "api"
    
    def execute(self, params: Dict) -> Dict:
        action = params.get("action")
        base_url = os.getenv("AUTH_API_URL", "http://localhost:8092")
        
        if action == "health":
            resp = requests.get(f'{base_url}/api/auth/health')
            return resp.json()
        elif action == "login":
            resp = requests.post(f'{base_url}/api/auth/login',
                json={"username": params.get("username"), "password": params.get("password")})
            return resp.json()
        else:
            return {"error": f"Unknown action: {action}"}

skill = AuthSkill()
