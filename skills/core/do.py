"""通用执行技能 - 让 LLM 思考，系统执行"""

from lib.llm_agent import LLMAgent

class DoSkill:
    name = "do"
    description = "通用执行器：理解任何需求并自动完成"
    version = "1.0.0"
    category = "core"

    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        return LLMAgent.think_and_act(goal)

skill = DoSkill()
