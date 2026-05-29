from lib.smart_config import smart_config
"""转小写技能"""
class To_lowerSkill:
    name = "to_lower"
    description = "转小写"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        # 基础实现
        result = {"success": True, "message": "转小写执行成功", "input": params}
        
        # 特殊处理
        if "to_lower" == "power":
            a = params.get("a", 0)
            b = params.get("b", 1)
            result["result"] = a ** b
        elif "to_lower" == "mod":
            a = params.get("a", 0)
            b = params.get("b", 1)
            result["result"] = a % b
        elif "to_lower" == "sqrt":
            import math
            a = params.get("a", 0)
            result["result"] = math.sqrt(a) if a >= 0 else 0
        elif "to_lower" == "abs":
            a = params.get("a", 0)
            result["result"] = abs(a)
        elif "to_lower" in ["to_upper", "to_lower", "trim", "reverse"]:
            text = params.get("text", "")
            if "to_lower" == "to_upper":
                result["result"] = text.upper()
            elif "to_lower" == "to_lower":
                result["result"] = text.lower()
            elif "to_lower" == "trim":
                result["result"] = text.strip()
            elif "to_lower" == "reverse":
                result["result"] = text[::-1]
        
        return result

skill = To_lowerSkill()
