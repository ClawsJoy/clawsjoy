#!/usr/bin/env python3
"""CodeAgent v3.0 - 代码生成智能体"""

from typing import Dict, Optional

from core.agents.business.base_business_agent import BusinessAgent
from core.lib.smart_adapter import smart_adapter


class CodeAgent(BusinessAgent):
    """代码生成智能体"""

    name = "code_agent"
    description = "代码生成与审查"
    version = "3.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"💻 CodeAgent v3.0 已上线")

    # 实现抽象方法 process（SmartAgent 要求）
    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        """代码生成业务（BusinessAgent 要求）"""

        language = self._detect_language(user_input)
        code = self._generate_code(user_input, language)

        if not self._code_safe(code):
            return {"success": False, "response": "生成的代码可能不安全，已拒绝执行。"}

        return {
            "success": True,
            "response": f"```{language}\n{code}\n```",
            "language": language,
        }

    def _detect_language(self, user_input: str) -> str:
        user_lower = user_input.lower()
        if "python" in user_lower:
            return "python"
        if "javascript" in user_lower:
            return "javascript"
        if "java" in user_lower:
            return "java"
        return "python"

    def _generate_code(self, user_input: str, language: str) -> str:
        prompt = f"请用 {language} 实现：{user_input}\n只输出代码，不要解释。"
        try:
            return smart_adapter.generate(prompt, auto_select=True)
        except:
            return f'print("Hello, World!")'

    def _code_safe(self, code: str) -> bool:
        dangerous = ["os.system", "subprocess", "eval", "exec", "__import__", "rm -rf"]
        for d in dangerous:
            if d in code:
                return False
        return True

