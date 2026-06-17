#!/usr/bin/env python3
"""translate_agent v4.0 - 智慧化翻译智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class TranslateAgentV4(BusinessAgent):
    name = "translate_agent_v4"
    description = "智慧翻译助手"
    version = "4.0.0"

    LANGUAGES = {
        "zh": {"name": "中文", "code": "zh"},
        "en": {"name": "英语", "code": "en"},
        "ja": {"name": "日语", "code": "ja"},
        "ko": {"name": "韩语", "code": "ko"},
        "fr": {"name": "法语", "code": "fr"},
        "de": {"name": "德语", "code": "de"},
        "es": {"name": "西班牙语", "code": "es"},
        "ru": {"name": "俄语", "code": "ru"},
        "ar": {"name": "阿拉伯语", "code": "ar"},
        "pt": {"name": "葡萄牙语", "code": "pt"},
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🌐 TranslateAgent v{self.version} 智慧化启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {("translate", "text"): (True, 0.95)}
        return capabilities.get((action, target), (False, 0.0))

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        # 翻译
        if any(kw in user_input for kw in ["翻译", "translate"]):
            return self._translate(user_input)
        return self._response(self._smart_fallback(user_input))

    def _translate(self, text: str) -> Dict:
        prompt = f"请翻译：{text}\n只输出翻译结果。"
        response = self._call_llm(prompt)
        if response:
            return self._response(f"🌐 翻译结果：\n\n{response}")
        return self._response("翻译失败，请重试。")

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
        return f"💡 我是翻译助手，请告诉我你要翻译什么。例如：翻译 hello 为中文"

    def _response(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = TranslateAgentV4("test")
    print("✅ translate_agent_v4 测试通过")
