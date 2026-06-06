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

