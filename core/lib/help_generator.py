#!/usr/bin/env python3
"""统一的帮助信息生成器 - 减少硬编码"""

import requests
from typing import Dict, Any


class HelpGenerator:
    """帮助信息生成器"""

    def __init__(self, agent_name: str, agent_description: str, capabilities: list):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.capabilities = capabilities

    def generate(self, user_input: str = None) -> str:
        """生成帮助信息"""
        # 如果有用户输入，尝试用 LLM 生成个性化回复
        if user_input:
            return self._llm_help(user_input)
        
        # 降级：生成简洁的帮助
        return self._simple_help()

    def _llm_help(self, user_input: str) -> str:
        """使用 LLM 生成帮助"""
        try:
            prompt = f"""用户说: {user_input}

我是 {self.agent_name}，{self.agent_description}。
我能做: {', '.join(self.capabilities[:5])}

请用简短友好的方式，告诉用户我能帮他做什么。
不要使用列表，用自然段落回答。"""

            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:1.5b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 100}
                },
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get("response", self._simple_help())
        except:
            pass
        return self._simple_help()

    def _simple_help(self) -> str:
        """简洁帮助（降级方案）"""
        return f"💡 {self.agent_name} 可以帮你：{', '.join(self.capabilities[:3])}"


# 全局实例
help_generator = HelpGenerator
