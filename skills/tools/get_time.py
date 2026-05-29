"""
get_time 技能 - 获取当前时间
"""

from datetime import datetime

class GetTimeSkill:
    """获取时间技能"""
    
    def __init__(self):
        self.name = "get_time"
        self.version = "1.0.0"
    
    def execute(self, params: dict) -> dict:
        """获取当前时间"""
        format_str = params.get('format', '%Y-%m-%d %H:%M:%S')
        result = datetime.now().strftime(format_str)
        return {
            "success": True,
            "result": result,
            "message": f"当前时间: {result}"
        }

skill = GetTimeSkill()
