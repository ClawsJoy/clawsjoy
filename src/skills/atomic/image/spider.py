from lib.smart_config import smart_config
"""spider技能"""
class SpiderSkill:
    name = "spider"
    description = "spider处理"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        return {"success": True, "message": "spider 执行成功", "input": params}

skill = SpiderSkill()
