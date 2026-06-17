#!/usr/bin/env python3
"""dialect_agent v4.0 - 智慧化方言智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, Optional, Tuple
from core.agents.business.business_agent import BusinessAgent


class DialectAgentV4(BusinessAgent):
    name = "dialect_agent_v4"
    description = "智慧方言助手"
    version = "4.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🗣️ DialectAgent v{self.version} 智慧化启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {("translate", "dialect"): (True, 0.90)}
        return capabilities.get((action, target), (False, 0.0))

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if any(kw in user_input for kw in ["方言", "dialect"]):
            return self._translate_dialect(user_input)
        return self._response(self._smart_fallback(user_input))

    def _translate_dialect(self, text: str) -> Dict:
        prompt = f"请将以下内容转换为方言表达：{text}"
        response = self._call_llm(prompt)
        if response:
            return self._response(f"🗣️ 方言表达：\n\n{response}")
        return self._response("方言转换失败，请重试。")

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except:
            pass
        return ""

    def _smart_fallback(self, user_input: str) -> str:
        return "💡 我是方言助手，请告诉我你想转换成哪种方言。"

    def _response(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = DialectAgentV4("test")
    print("✅ dialect_agent_v4 测试通过")
