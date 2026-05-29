from lib.smart_config import smart_config
"""remove_bg技能"""
class Remove_bgSkill:
    name = "remove_bg"
    description = "remove_bg处理"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        return {"success": True, "message": "remove_bg 执行成功", "input": params}

skill = Remove_bgSkill()
