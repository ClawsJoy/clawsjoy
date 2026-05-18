"""Code Agent - 代码助手"""

from agents.base_agent import BaseAgent

class CodeAgent(BaseAgent):
    name = "code_agent"
    description = "代码助手 - 生成和解释代码"
    version = "2.0.0"
    type = "custom"
    
    capabilities = [
        {
            "name": "code_generation",
            "description": "根据需求生成代码",
            "skills": ["code_agent_v7", "script_generator"],
            "examples": ["写一个加法函数", "生成Python脚本"]
        },
        {
            "name": "code_review",
            "description": "代码审查和优化建议",
            "skills": ["code_agent_v7"],
            "examples": ["审查这段代码", "优化性能"]
        },
        {
            "name": "code_debug",
            "description": "代码调试和错误修复",
            "skills": ["self_debug", "error_analyzer"],
            "examples": ["修复这个bug", "分析错误原因"]
        }
    ]
    
    personality = {
        "style": "technical",
        "language": "zh-CN",
        "tone": "precise",
        "greeting": "你好，我是代码助手，可以帮你写代码、审查代码、调试程序。"
    }
    
    def __init__(self):
        super().__init__(
            agent_id="code_agent",
            config={
                "name": "代码助手",
                "type": "custom",
                "personality": "technical",
                "capabilities": self.capabilities
            }
        )
        self.remember("Code Agent 已启动", shared=True)
    
    def execute(self, params):
        requirement = params.get("requirement", "")
        if not requirement:
            return {"success": False, "error": "需要提供需求"}
        
        self.remember(f"代码需求: {requirement[:50]}", shared=True)
        
        from skills.code_agent_v7 import skill
        return skill.execute({"requirement": requirement})

code_agent = CodeAgent()
