from lib.smart_config import smart_config
"""数字取整"""
class RoundSkill:
    name = "round"
    description = "数字取整"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        value = params.get("value", 0)
        decimals = params.get("decimals", 0)
        result = round(value, decimals)
        return {"success": True, "original": value, "rounded": result, "decimals": decimals}

skill = RoundSkill()
