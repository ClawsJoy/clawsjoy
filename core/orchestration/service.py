"""独立编排服务 - 不依赖 Orchestrator"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from typing import Dict

from core.orchestration.config_planner import config_planner
from engine.orchestration.task_manager import task_manager


class OrchestrationService:
    """独立编排服务"""

    def __init__(self):
        self.task_manager = task_manager
        self.planner = config_planner

    def execute(self, user_input: str, user_id: str = "default") -> Dict:
        tasks = self.planner.create_tasks(user_input)
        if not tasks:
            return {"success": False, "error": "无法生成任务计划"}

        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append(
                {
                    "name": task.get("name"),
                    "agent": task.get("agent"),
                    "params": task.get("params", {}),
                    "depends_on": task.get("depends_on", []),
                    "optional": task.get("optional", False),
                }
            )

        plan = self.task_manager.create_plan(
            name="编排任务", description=user_input[:100], tasks=formatted_tasks
        )

        def get_agent(agent_name: str):
            return self._get_agent(agent_name, user_id)

        result = self.task_manager.execute_plan_parallel(plan.id, get_agent)

        return {
            "success": result.get("success", False),
            "plan_id": plan.id,
            "results": result.get("results", []),
        }

    def _get_agent(self, agent_name: str, user_id: str):
        try:
            if agent_name == "video_agent":
                from agents.video_agent.agent import VideoAgent

                return VideoAgent(user_id)
            elif agent_name == "vision_agent":
                from agents.vision_agent.agent import VisionAgent

                return VisionAgent(user_id)
            elif agent_name == "writer_agent":
                from agents.writer_agent.agent import WriterAgent

                return WriterAgent(user_id)
            elif agent_name == "analysis_agent":
                from agents.analysis_agent.agent import AnalysisAgent

                return AnalysisAgent(user_id)
            else:
                from agents.chat_agent.agent import ChatAgent

                return ChatAgent(user_id)
        except Exception as e:
            print(f"获取 Agent {agent_name} 失败: {e}")
            return None


orchestration_service = OrchestrationService()


if __name__ == "__main__":
    result = orchestration_service.execute("帮我制作一个关于AI的视频")
    print(f"成功: {result.get('success')}")
    for r in result.get("results", []):
        print(f"  {r.get('task')}: {r.get('response', '')[:50]}")
