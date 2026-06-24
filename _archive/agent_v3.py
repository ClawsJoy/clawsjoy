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
        self.supported_languages = ["python", "javascript", "java", "go", "rust"]
        print(f"💻 CodeAgent v3.0 已上线")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        """代码生成业务"""

        # 1. 识别编程语言
        language = self._detect_language(user_input)

        # 2. 生成代码
        code = self._generate_code(user_input, language)

        # 3. 安全检查
        if not self._code_safe(code):
            return {
                "success": False,
                "response": "生成的代码可能不安全，已拒绝执行。",
            }

        return {
            "success": True,
            "response": f"```{language}\n{code}\n```",
            "language": language,
            "code": code,
        }

    def _detect_language(self, user_input: str) -> str:
        """检测编程语言"""
        user_lower = user_input.lower()
        if "python" in user_lower:
            return "python"
        if "javascript" in user_lower or "js" in user_lower:
            return "javascript"
        if "java" in user_lower:
            return "java"
        if "go" in user_lower or "golang" in user_lower:
            return "go"
        if "rust" in user_lower:
            return "rust"
        return "python"

    def _generate_code(self, user_input: str, language: str) -> str:
        """生成代码"""
        prompt = f"""请用 {language} 语言实现以下需求，只输出代码，不要解释：

{user_input}"""
        try:
            return smart_adapter.generate(prompt, auto_select=True)
        except Exception as e:
            return f"# 代码生成失败: {e}\nprint('Hello, World!')"

    def _code_safe(self, code: str) -> bool:
        """代码安全检查"""
        dangerous = ["os.system", "subprocess", "eval", "exec", "__import__", "rm -rf"]
        for pattern in dangerous:
            if pattern in code:
                return False
        return True


code_agent = CodeAgent()
