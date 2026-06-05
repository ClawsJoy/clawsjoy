#!/usr/bin/env python3
"""翻译智能体 - 增强版（多语言互译）"""

import re
from typing import Dict, List, Optional

from core.agents.business.base_business_agent import BusinessAgent
from core.lib.smart_adapter import smart_adapter


class TranslateAgent(BusinessAgent):
    name = "translate_agent"
    description = "多语言智能翻译"
    version = "3.0.0"

    # 完整语言映射
    LANG_MAP = {
        "中文": "zh",
        "汉语": "zh",
        "Chinese": "zh",
        "英文": "en",
        "英语": "en",
        "English": "en",
        "日文": "ja",
        "日语": "ja",
        "Japanese": "ja",
        "韩文": "ko",
        "韩语": "ko",
        "Korean": "ko",
        "法文": "fr",
        "法语": "fr",
        "French": "fr",
        "德文": "de",
        "德语": "de",
        "German": "de",
        "西班牙文": "es",
        "西班牙语": "es",
        "Spanish": "es",
        "俄文": "ru",
        "俄语": "ru",
        "Russian": "ru",
        "意大利文": "it",
        "意大利语": "it",
        "Italian": "it",
        "葡萄牙文": "pt",
        "葡萄牙语": "pt",
        "Portuguese": "pt",
        "阿拉伯文": "ar",
        "阿拉伯语": "ar",
        "Arabic": "ar",
        "荷兰文": "nl",
        "荷兰语": "nl",
        "Dutch": "nl",
        "瑞典文": "sv",
        "瑞典语": "sv",
        "Swedish": "sv",
        "波兰文": "pl",
        "波兰语": "pl",
        "Polish": "pl",
        "土耳其文": "tr",
        "土耳其语": "tr",
        "Turkish": "tr",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.translation_history = []
        print(f"🌐 翻译智能体 v3.0 已上线")

    def _execute_business(self, user_input: str, context: dict = None) -> dict:
        """业务逻辑实现 - BusinessAgent 要求"""
        return self.process(user_input, context)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[翻译] 收到: {user_input}")

        # 1. 多语言互译
        match = re.search(r"把(.+)翻译成(\w+)", user_input)
        if match:
            text = match.group(1).strip()
            target = match.group(2)
            return self._translate(text, target)

        # 2. 翻译成指定语言
        for lang, code in self.LANG_MAP.items():
            if (
                f"翻译成{lang}" in user_input
                or f"译成{lang}" in user_input
                or f"to {lang}" in user_input.lower()
            ):
                text = self._extract_text(user_input)
                if text:
                    result = self._translate(text, code)
                    return self._build_response(result, text, lang)

        # 3. 自动检测语言并翻译成中文
        if "翻译" in user_input:
            text = self._extract_text(user_input)
            if text:
                result = self._translate(text, "zh")
                return self._build_response(result, text, "中文")

        # 4. 批量翻译
        if "批量翻译" in user_input:
            texts = self._extract_batch_texts(user_input)
            if texts:
                results = self._batch_translate(texts)
                return self._batch_response(results)

        # 5. 语言检测
        if "检测语言" in user_input:
            text = self._extract_text(user_input)
            if text:
                detected = self._detect_language(text)
                return {
                    "success": True,
                    "response": f"🔍 检测到语言：{detected}",
                    "detected_language": detected,
                    "agent": self.name,
                    "user_id": self.user_id,
                }

        return self._help()

    def _extract_text(self, text: str) -> Optional[str]:
        """提取待翻译文本"""
        patterns = [
            r"翻译(?:成\w+)?\s+(.+)$",
            r"译成\w+\s+(.+)$",
            r"translate\s+(.+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_batch_texts(self, text: str) -> List[str]:
        """提取批量文本"""
        lines = text.split("\n")
        texts = []
        for line in lines:
            if line.strip() and not line.startswith(("批量", "翻译")):
                texts.append(line.strip())
        return texts

    def _translate(self, text: str, target: str) -> str:
        """执行翻译"""
        try:
            prompt = f"""请将以下文本翻译成{target}，只输出翻译结果，不要任何解释：

原文：{text}

翻译结果："""
            result = smart_adapter.generate(prompt, auto_select=True).strip()
            # 记录历史
            self.translation_history.append(
                {
                    "original": text,
                    "translated": result,
                    "target": target,
                    "timestamp": __import__("time").time(),
                }
            )
            # 保留最近50条
            if len(self.translation_history) > 50:
                self.translation_history = self.translation_history[-50:]
            return result
        except Exception as e:
            return f"[翻译失败] {text}"

    def _batch_translate(self, texts: List[str]) -> List[Dict]:
        """批量翻译"""
        results = []
        for text in texts:
            translated = self._translate(text, "zh")
            results.append({"original": text, "translated": translated})
        return results

    def _detect_language(self, text: str) -> str:
        """检测语言"""
        for lang, code in self.LANG_MAP.items():
            if len(lang) <= 4:
                continue
        return "未知"

    def _build_response(self, result: str, original: str, target_lang: str) -> Dict:
        """构建响应"""
        return {
            "success": True,
            "response": f"🌐 {target_lang}：{result}",
            "original": original,
            "translated": result,
            "target_language": target_lang,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _batch_response(self, results: List[Dict]) -> Dict:
        """批量翻译响应"""
        summary = f"📚 批量翻译完成，共 {len(results)} 条：\n"
        for r in results:
            summary += f"• {r['original'][:30]} → {r['translated'][:30]}\n"
        return {
            "success": True,
            "response": summary,
            "results": results,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _help(self) -> Dict:
        """帮助信息"""
        return {
            "success": True,
            "response": f"🌐 翻译功能：\n• 说「翻译 Hello」\n• 说「把你好翻译成英文」\n• 说「批量翻译」\n支持 {len(self.LANG_MAP)} 种语言",
            "supported_languages": list(self.LANG_MAP.keys())[:10],
            "agent": self.name,
            "user_id": self.user_id,
        }
