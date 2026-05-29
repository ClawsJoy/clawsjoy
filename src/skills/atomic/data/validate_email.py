from lib.smart_config import smart_config
"""邮箱验证"""
import re

class ValidateEmailSkill:
    name = "validate_email"
    description = "验证邮箱格式"
    version = "1.0.0"
    category = "data"
    
    def execute(self, params):
        email = params.get("email", "")
        if not email:
            return {"success": False, "error": "需要提供邮箱"}
        
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        is_valid = bool(re.match(pattern, email))
        
        return {
            "success": True,
            "email": email,
            "is_valid": is_valid,
            "message": "邮箱格式正确" if is_valid else "邮箱格式错误"
        }

skill = ValidateEmailSkill()
