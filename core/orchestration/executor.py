"""编排执行器 - 整合 planner 和 task_manager"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

from core.orchestration.planner import TaskPlanner
from engine.orchestration.task_manager import task_manager
from engine.orchestration.user_friendly import UserFriendlyOrchestrator


class OrchestrationExecutor:
    """编排执行器 - 统一入口"""

    def __init__(self):
        self.planner = TaskPlanner()
        self.task_manager = task_manager
        self.user_orchestrator = None

    def execute(self, user_input: str, user_id: str = "default") -> dict:
        """执行编排任务"""

        # 1. 生成计划
        plan = self.planner.plan(user_input)
        if not plan.get("success"):
            return {"success": False, "error": "无法生成计划"}

        tasks = plan.get("tasks", [])
        print(f"[编排] 生成 {len(tasks)} 个任务")

        # 2. 转换为 task_manager 格式
        task_list = []
        for i, task in enumerate(tasks):
            task_list.append(
                {
                    "name": task.get("name", f"task_{i}"),
                    "agent": task.get("agent", "executor_agent"),
                    "action": task.get("action", "process"),
                    "params": {"message": task.get("message", "")},
                    "depends_on": [],
                    "checkpoint": i == 0,  # 第一个任务作为检查点
                }
            )

        # 3. 创建编排计划
        orchestration_plan = self.task_manager.create_plan(
            name=plan.get("name", "未命名任务"), description=user_input, tasks=task_list
        )

        # 4. 定义 Agent 获取函数
        def get_agent(agent_name: str):
            return self._get_agent(agent_name, user_id)

        # 5. 执行计划
        result = self.task_manager.execute_plan(orchestration_plan.id, get_agent)

        return {
            "success": result.get("success", False),
            "plan_id": orchestration_plan.id,
            "plan_name": plan.get("name"),
            "tasks": tasks,
            "execution_result": result,
        }

    def _get_agent(self, agent_name: str, user_id: str):
        """获取 Agent 实例"""
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
                from agents.executor_agent.agent import ExecutorAgent

                return ExecutorAgent(user_id)
        except Exception as e:
            print(f"获取 Agent {agent_name} 失败: {e}")
            return None

    def get_status(self, plan_id: str) -> dict:
        """获取执行状态"""
        return self.task_manager.get_plan_status(plan_id)


# 全局实例
orchestration_executor = OrchestrationExecutor()


if __name__ == "__main__":
    # 测试
    result = orchestration_executor.execute("帮我制作一个关于AI的视频", "test")
    print(f"执行结果: {result.get('success')}")
    print(f"计划ID: {result.get('plan_id')}")
    print(f"计划名称: {result.get('plan_name')}")
