import logging

"""翻译 Agent - 支持多语言"""

import re
from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class TranslateAgent(SmartAgent):
        import requests
    """翻译助手 - 支持多语言"""

    name = "translate_agent"
    description = "多语言翻译助手"
    type = "custom"

    LANGUAGE_MAP = {
        "中文": "zh",
        "英文": "en",
        "英语": "en",
        "日文": "ja",
        "日语": "ja",
        "韩文": "ko",
        "韩语": "ko",
        "法文": "fr",
        "法语": "fr",
        "德文": "de",
        "德语": "de",
        "西班牙文": "es",
        "西班牙语": "es",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🌐 翻译Agent 初始化完成")

    def process(self, user_input: str, context=None) -> Dict:
        # 提取要翻译的文本
        text = user_input

        # 检测目标语言
        target_lang = "中文"  # 默认
        for lang in self.LANGUAGE_MAP:
            if f"到{lang}" in user_input or f"翻译成{lang}" in user_input:
                target_lang = lang
                text = text.replace(f"到{lang}", "").replace(f"翻译成{lang}", "")
                break

        # 清理文本
        text = re.sub(r'^(翻译|请翻译|帮我翻译)', '', text).strip()

        if not text:
            text = user_input

        # 构建 prompt
        prompt = f"请将以下内容翻译成{target_lang}，只输出翻译结果：\n{text}"

        try:
            response = smart_adapter.generate(prompt, auto_select=True)
        except Exception as e:
            response = f"翻译失败: {e}"

        return {
            "success": True,
            "response": response.strip(),
            "target_lang": target_lang,
            "agent": self.name,
            "user_id": self.user_id
        }


translate_agent = TranslateAgent()
