"""内容创作 Agent"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agents.base_agent import BaseAgent

class ContentAgent(BaseAgent):
    name = "content_agent"
    description = "内容创作专家，生成文章、脚本、文案"
    capabilities = ["content_generation", "script_writing", "copywriting", "translation"]
    skills = ["hot_dual_script", "text_processor", "prompt_optimizer"]
    
    def execute(self, params):
        operation = params.get("operation")
        topic = params.get("topic", "")
        
        if operation == "script":
            return self._generate_script(topic)
        elif operation == "article":
            return self._generate_article(topic)
        elif operation == "optimize":
            return self._optimize_text(params.get("text"))
        return {"success": False, "error": "未知操作"}
    
    def _generate_script(self, topic):
        from skills.hot_dual_script import skill
        result = skill.execute({"topic": topic})
        return {"success": True, "script": result.get("narration", "")}
    
    def _generate_article(self, topic):
        # 简化实现，实际可调用 LLM
        return {"success": True, "article": f"关于 {topic} 的原创文章内容..."}
    
    def _optimize_text(self, text):
        from skills.prompt_optimizer import skill
        result = skill.execute({"text": text})
        return {"success": True, "optimized": result.get("result", text)}

content_agent = ContentAgent()
