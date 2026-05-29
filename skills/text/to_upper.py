"""
to_upper 技能 - 字符串转大写
"""

class ToUpperSkill:
    """转大写技能"""
    
    def __init__(self):
        self.name = "to_upper"
        self.version = "1.0.0"
    
    def execute(self, params: dict) -> dict:
        """将字符串转为大写"""
        text = params.get('text', '')
        result = text.upper()
        return {
            "success": True,
            "result": result,
            "message": f"'{text}' -> '{result}'"
        }

skill = ToUpperSkill()
