"""质量门 - 逐环节检验"""
from lib.memory_simple import memory

class QualityGateSkill:
    name = "quality_gate"
    description = "逐环节质量检验"
    version = "1.0.0"
    category = "quality"

    STANDARDS = {
        "intent_parsing": {
            "check": lambda r: r.get("topic") and len(r.get("topic", "")) > 2,
            "retry_msg": "主题提取失败"
        },
        "script": {
            "check": lambda r: len(r.get("script", "")) > 50,
            "retry_msg": "脚本太短"
        },
        "background": {
            "check": lambda r: len(r.get("images", [])) >= 2,
            "retry_msg": "背景图不足"
        },
        "audio": {
            "check": lambda r: r.get("duration", 0) >= 10,
            "retry_msg": "音频太短"
        },
        "video": {
            "check": lambda r: r.get("success", False) and r.get("duration", 0) > 0,
            "retry_msg": "视频合成失败"
        }
    }

    def execute(self, params):
        stage = params.get("stage", "")
        result = params.get("result", {})
        
        if stage not in self.STANDARDS:
            return {"pass": True, "message": "未知环节，默认通过"}
        
        standard = self.STANDARDS[stage]
        is_pass = standard["check"](result)
        
        # 记录到记忆
        memory.remember(
            f"quality_gate|{stage}|pass:{is_pass}|msg:{standard['retry_msg'] if not is_pass else '合格'}",
            category="quality_gate"
        )
        
        return {
            "pass": is_pass,
            "message": standard["retry_msg"] if not is_pass else f"{stage}合格",
            "stage": stage
        }

skill = QualityGateSkill()
