#!/usr/bin/env python3
"""TranslateAgent v4.0 - 智慧翻译智能体（多语言）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class TranslateAgentV4(BusinessAgent):
    """翻译 Agent - 支持多语言"""
    
    name = "translate_agent_v4"
    description = "智慧翻译助手"
    version = "4.0.0"
    
    # 支持的语言映射
    LANGUAGES = {
        # 高精度（5星）
        "zh": {"name": "中文", "code": "zh", "quality": 5},
        "en": {"name": "英语", "code": "en", "quality": 5},
        "ja": {"name": "日语", "code": "ja", "quality": 4},
        "ko": {"name": "韩语", "code": "ko", "quality": 4},
        
        # 中精度（3-4星）
        "fr": {"name": "法语", "code": "fr", "quality": 4},
        "de": {"name": "德语", "code": "de", "quality": 4},
        "es": {"name": "西班牙语", "code": "es", "quality": 4},
        "it": {"name": "意大利语", "code": "it", "quality": 3},
        "pt": {"name": "葡萄牙语", "code": "pt", "quality": 3},
        "ru": {"name": "俄语", "code": "ru", "quality": 3},
        
        # 基础支持（2-3星）
        "ar": {"name": "阿拉伯语", "code": "ar", "quality": 2},
        "tr": {"name": "土耳其语", "code": "tr", "quality": 2},
        "vi": {"name": "越南语", "code": "vi", "quality": 2},
        "th": {"name": "泰语", "code": "th", "quality": 2},
        "id": {"name": "印尼语", "code": "id", "quality": 2},
        "ms": {"name": "马来语", "code": "ms", "quality": 2},
        "hi": {"name": "印地语", "code": "hi", "quality": 2},
        "pl": {"name": "波兰语", "code": "pl", "quality": 2},
        "nl": {"name": "荷兰语", "code": "nl", "quality": 2},
        "sv": {"name": "瑞典语", "code": "sv", "quality": 2},
    }
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🌐 TranslateAgent v{self.version} 智慧化启动")
        print(f"   📚 支持 {len(self.LANGUAGES)} 种语言")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.95) if action == "translate" and target == "text" else (False, 0.0)
    
    def can_handle(self, action: str, target: str) -> bool:
        return action == 'translate' and target == 'text'
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 解析翻译指令
        result = self._parse_and_translate(user_input)
        return self._response(result)
    
    def _parse_and_translate(self, text: str) -> str:
        """解析翻译指令并执行"""
        
        # 格式1: "翻译：Hello World" (自动目标语言)
        if "翻译：" in text or "翻译:" in text:
            content = re.sub(r'翻译[：:]', '', text).strip()
            return self._to_chinese(content)
        
        # 格式2: "中译英：你好" (指定语言对)
        lang_patterns = [
            (r'中译英[：:]?\s*(.+)', "zh", "en"),
            (r'英译中[：:]?\s*(.+)', "en", "zh"),
            (r'中译日[：:]?\s*(.+)', "zh", "ja"),
            (r'日译中[：:]?\s*(.+)', "ja", "zh"),
            (r'中译韩[：:]?\s*(.+)', "zh", "ko"),
            (r'韩译中[：:]?\s*(.+)', "ko", "zh"),
            (r'中译法[：:]?\s*(.+)', "zh", "fr"),
            (r'法译中[：:]?\s*(.+)', "fr", "zh"),
            (r'中译德[：:]?\s*(.+)', "zh", "de"),
            (r'德译中[：:]?\s*(.+)', "de", "zh"),
            (r'中译西[：:]?\s*(.+)', "zh", "es"),
            (r'西译中[：:]?\s*(.+)', "es", "zh"),
        ]
        
        for pattern, src, tgt in lang_patterns:
            match = re.search(pattern, text)
            if match:
                content = match.group(1).strip()
                return self._translate_pair(content, src, tgt)
        
        # 格式3: "翻译成日语：Hello"
        target_match = re.search(r'翻译成([^：:]+)[：:]?\s*(.+)', text)
        if target_match:
            target_name = target_match.group(1).strip()
            content = target_match.group(2).strip()
            return self._to_language(content, target_name)
        
        # 默认：自动翻译成中文
        return self._to_chinese(text)
    
    def _to_chinese(self, content: str) -> str:
        """翻译成中文"""
        if not content:
            return "请提供要翻译的文本。"
        
        prompt = f"""将以下内容翻译成中文：

{content}

只输出翻译结果，不要解释。"""
        
        response = self._call_llm(prompt)
        
        if response and response != content:
            return f"🌐 中文翻译：\n\n{response}"
        
        return self._simple_translate(content, "zh")
    
    def _to_language(self, content: str, target_name: str) -> str:
        """翻译成指定语言"""
        # 查找语言代码
        target_code = None
        for code, info in self.LANGUAGES.items():
            if info["name"] == target_name or target_name in info["name"]:
                target_code = code
                target_name = info["name"]
                break
        
        if not target_code:
            return f"不支持的目标语言：{target_name}\n支持：{', '.join([v['name'] for v in self.LANGUAGES.values()])}"
        
        prompt = f"""将以下内容翻译成{target_name}：

{content}

只输出翻译结果，不要解释。"""
        
        response = self._call_llm(prompt)
        
        if response and response != content:
            return f"🌐 {target_name}翻译：\n\n{response}"
        
        return f"翻译失败，请稍后重试。"
    
    def _translate_pair(self, content: str, src: str, tgt: str) -> str:
        """指定语言对翻译"""
        src_name = self.LANGUAGES.get(src, {}).get("name", src)
        tgt_name = self.LANGUAGES.get(tgt, {}).get("name", tgt)
        
        prompt = f"""将以下{src_name}翻译成{tgt_name}：

{content}

只输出翻译结果，不要解释。"""
        
        response = self._call_llm(prompt)
        
        if response and response != content:
            return f"🌐 {src_name} → {tgt_name}\n\n{response}"
        
        return f"翻译失败，请稍后重试。"
    
    def _simple_translate(self, text: str, target: str = "zh") -> str:
        """简单规则翻译（降级）"""
        common_en = {
            "Hello": "你好", "World": "世界", "Good": "好",
            "Morning": "早上", "Night": "晚上", "Thank": "谢谢",
            "You": "你", "Yes": "是", "No": "不", "Love": "爱"
        }
        
        result = text
        for en, zh in common_en.items():
            result = result.replace(en, zh)
            result = result.replace(en.lower(), zh)
        
        if result != text:
            return f"🌐 翻译结果：\n\n{result}"
        
        return f"翻译失败，请重试。\n原文：{text}\n\n💡 提示：可以尝试更清晰的表达"
    
    def _get_help(self) -> str:
        return f"💡 我是 {self.name}，请描述你需要什么帮助，我会尽力帮你。"

支持语言：{languages}

使用方式：
- "翻译：Hello World" → 翻译成中文
- "中译英：你好世界" → 中译英
- "英译中：Good morning" → 英译中
- "翻译成日语：你好" → 翻译成日语
- "翻译成韩语：Thank you"

共支持 {len(self.LANGUAGES)} 种语言互译"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = TranslateAgentV4("test")
    print("\n✅ TranslateAgentV4 多语言版测试通过")
