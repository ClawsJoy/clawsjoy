"""ExecutorAgent - 执行层"""

from typing import Dict, Optional

from core.agents.business.base_business_agent import BusinessAgent


class ExecutorAgent(BusinessAgent):
    name = "executor_agent"
    description = "任务执行器"
    version = "2.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"⚙️ ExecutorAgent v{self.version} 已上线")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        return self.process(user_input, context)

    def process(self, user_input: str, context: Dict = None) -> Dict:
        print(f"[执行器] 执行: {user_input[:50]}...")

        result = self._call_do_anything(user_input)
        print(f"[执行器] do_anything 返回: {result}")

        # 获取响应文本
        response = result.get("response")
        if response is None:
            response = result.get("result")
        if response is None:
            response = "执行完成"

        if not isinstance(response, str):
            response = str(response)

        print(f"[执行器] 最终响应: {response[:50]}...")
        print(f"[执行器] 返回 agent: {self.name}")

        return {
            "success": True,
            "response": response,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _call_do_anything(self, task: str) -> Dict:
        from skills.core.do_anything import skill

        return skill.execute({"goal": task})


executor_agent = ExecutorAgent()
