#!/usr/bin/env python3
"""TranslateAgent v4.2 - 精简稳定版（翻译）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class TranslateAgentV4(BusinessAgent):
    """翻译 Agent - 精简稳定版"""

    name = "translate_agent_v4"
    description = "智慧翻译助手"
    version = "4.2.0"

    LANGUAGES = {
        "zh": "中文", "en": "英语", "ja": "日语", "ko": "韩语",
        "fr": "法语", "de": "德语", "es": "西班牙语", "ru": "俄语",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🌐 TranslateAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心翻译逻辑"""
        t = user_input.lower()
        
        # 检测目标语言
        target_lang = "中文"
        for code, name in self.LANGUAGES.items():
            if code in t or name in t:
                target_lang = name
                break
        
        # 提取待翻译文本
        text = re.sub(r'^(翻译|翻译成|译成|转成|转换成)', '', user_input).strip()
        text = re.sub(r'[中英日韩法德西俄]+\s*[文语]?\s*$', '', text).strip()
        
        if not text:
            return self._resp("请提供要翻译的内容。例如：翻译 hello 成中文")
        
        prompt = f"将以下内容翻译成{target_lang}，只输出翻译结果：{text}"
        result = self._call_llm(prompt)
        
        return self._resp(f"🌐 翻译结果（{target_lang}）：\n\n{result}") if result else self._resp("翻译失败，请重试。")

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 256}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[Translate] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = TranslateAgentV4("test")
    print(agent.process("翻译 hello 成中文")["response"])
