"""
获取当前时间
"""
class Get_timeSkill:
    name = "get_time"
    description = "获取当前时间"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from datetime import datetime; result = datetime.now().isoformat()
        return {"success": True, "result": result}

skill = Get_timeSkill()
