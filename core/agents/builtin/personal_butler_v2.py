"""私人管家 v2.0 - 用户入口"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class PersonalButlerV2(SmartAgent):
    """私人管家 - 用户入口"""

    name = "personal_butler_v2"
    description = "智能私人管家"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"👤 私人管家 已启动")

    def process(self, user_input: str, context=None) -> Dict:
        print(f"[管家] 收到: {user_input}")
        print(f"[管家] 调用 http_call 到 decision_agent")
        result = self.http_call("decision_agent", user_input)
        print(f"[管家] http_call 返回: {result}")
        return result


personal_butler = PersonalButlerV2()
