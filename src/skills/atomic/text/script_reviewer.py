from lib.smart_config import smart_config
"""脚本审核器 - 检查脚本质量"""
class ScriptReviewerSkill:
    name = "script_reviewer"
    description = "审核脚本质量"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        script = params.get("script", "")
        
        if not script:
            return {"success": False, "error": "需要提供脚本"}
        
        issues = []
        if len(script) < 50:
            issues.append("脚本太短，建议50字以上")
        if len(script) > 300:
            issues.append("脚本太长，建议300字以内")
        if "..." in script:
            issues.append("脚本包含省略号，可能不完整")
        
        return {
            "success": len(issues) == 0,
            "script_length": len(script),
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 20)
        }

skill = ScriptReviewerSkill()
