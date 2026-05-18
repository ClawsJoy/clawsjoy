"""Orchestrator Agent - 任务编排器"""

from agents.base_agent import BaseAgent

class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "任务编排器 - 负责任务拆解和调度"
    version = "2.0.0"
    type = "core"
    
    capabilities = [
        {
            "name": "task_planning",
            "description": "任务规划，将复杂目标拆解为可执行步骤",
            "skills": ["do_anything", "task_planner"],
            "examples": ["制作香港介绍视频", "生成AI图片并发布"]
        },
        {
            "name": "skill_orchestration",
            "description": "技能编排，按顺序调用多个技能",
            "skills": ["closed_loop_executor", "workflow_engine"],
            "examples": ["先采集图片，再制作视频，最后上传"]
        },
        {
            "name": "workflow_management",
            "description": "工作流管理，管理任务执行流程",
            "skills": ["user_task_executor"],
            "examples": ["批量处理任务队列"]
        }
    ]
    
    personality = {
        "style": "professional",
        "language": "zh-CN",
        "tone": "formal",
        "greeting": "您好，我是任务编排器，可以帮您规划和调度任务。"
    }
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            config={
                "name": "任务编排器",
                "type": "core",
                "personality": "professional",
                "capabilities": self.capabilities
            }
        )
        self.remember("Orchestrator Agent 已启动", shared=True)
    
    def execute(self, params):
        goal = params.get("goal", "")
        if not goal:
            return {"success": False, "error": "需要提供目标"}
        
        self.remember(f"收到任务: {goal[:50]}", shared=True)
        
        from skills.core.do_anything import skill
        result = skill.execute({"goal": goal})
        
        return result

orchestrator = OrchestratorAgent()
