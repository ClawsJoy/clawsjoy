"""WriterAgent - 业务层：内容创作"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

from typing import Dict, Optional

from core.agents.business.business_agent_v2 import BusinessAgentV2


class WriterAgent(BusinessAgentV2):
    """作家 - 业务层，执行写作任务"""

    name = "writer_agent"
    description = "智能写作助手"
    version = "3.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"✍️ 作家 v{self.version} 已上岗")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        return self.process(user_input, context)

