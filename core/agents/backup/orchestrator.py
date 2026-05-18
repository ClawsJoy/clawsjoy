"""Orchestrator Agent - 任务编排器"""

from agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "任务编排器 - 负责拆解和调度任务"
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            config={
                "name": "任务编排器",
                "type": "core",
                "capabilities": ["task_planning", "skill_orchestration", "workflow_management"],
                "personality": "professional",
                "endpoint": {"port": 5002, "health_path": "/api/health"}
            }
        )
        self.remember("Orchestrator Agent 已启动", shared=True)
    
    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        self.remember(f"收到任务: {goal[:50]}", shared=True)
        
        # 调用 do_anything 技能
        from skills.core.do_anything import skill
        result = skill.execute({"goal": goal})
        
        return result

orchestrator = OrchestratorAgent()
