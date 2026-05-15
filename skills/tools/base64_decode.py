"""
Base64解码
"""
class Base64_decodeSkill:
    name = "base64_decode"
    description = "Base64解码"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        import base64; data = params.get('data', ''); result = base64.b64decode(data).decode()
        return {"success": True, "result": result}

skill = Base64_decodeSkill()
