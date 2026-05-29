"""代码 Agent - 生成代码"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class CodeAgent(SmartAgent):
    """代码助手 Agent"""

    name = "code_agent"
    description = "代码生成与审查"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"💻 代码Agent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[代码] 收到: {user_input}")

        # 使用 LLM 生成代码
        prompt = f"""根据用户需求生成代码。

用户需求: {user_input}

要求:
1. 只输出代码，不要解释
2. 使用 ```python 标记代码块
3. 代码要完整可运行

输出:"""

        response = smart_adapter.generate(prompt, auto_select=True)

        return {
            "success": True,
            "response": response,
            "agent": self.name,
            "user_id": self.user_id
        }


# code_agent = CodeAgent()  # 注释：改为按需创建
