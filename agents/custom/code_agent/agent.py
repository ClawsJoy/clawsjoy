import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agents.base_agent import BaseAgent

class CodeAgent(BaseAgent):
    def __init__(self):
        super().__init__("code_agent", "custom")
    
    def execute(self, params):
        requirement = params.get("requirement", "")
        
        # 使用个性配置
        style = self.get_personality().get("style", "technical")
        
        # 调用 Code Agent 技能
        from skills.code_agent_v7 import skill
        result = skill.execute({"requirement": requirement})
        
        # 记录对话
        self.log_conversation(requirement, result.get("code", "")[:100])
        
        return result

# 创建实例
code_agent = CodeAgent()
