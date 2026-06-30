#!/usr/bin/env python3
"""DeepSeek API 适配器（OpenAI 兼容格式）"""

import requests
from . import BaseAdapter


class DeepSeekAdapter(BaseAdapter):
    """DeepSeek API 适配器"""

    endpoint = "https://api.deepseek.com/v1/chat/completions"

    def execute(self, prompt: str, system_prompt: str = "", history: list = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model or "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", self.count_tokens(prompt + content))
                return {"success": True, "content": content, "tokens": tokens, "model": self.model}
            else:
                return {"success": False, "content": f"API错误: {resp.status_code}", "tokens": 0, "model": self.model}
        except Exception as e:
            return {"success": False, "content": f"请求失败: {e}", "tokens": 0, "model": self.model}
