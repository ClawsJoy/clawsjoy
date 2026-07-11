#!/usr/bin/env python3
"""DeepSeek API 适配器（OpenAI 兼容格式）"""

import requests
from . import BaseAdapter


class DeepSeekAdapter(BaseAdapter):
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
                    "model": self.model or "deepseek-v4-flash",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return {"success": True, "content": content, "tokens": tokens, "model": self.model}
            else:
                return {"success": False, "content": f"API错误: {resp.status_code}", "tokens": 0, "model": self.model}
        except Exception as e:
            return {"success": False, "content": f"请求失败: {e}", "tokens": 0, "model": self.model}

    def execute_json(self, prompt: str, system_prompt: str = "") -> dict:
        """JSON Output 模式"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model or "deepseek-v4-flash",
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                    "max_tokens": 800,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return {"success": True, "content": content, "tokens": tokens, "model": self.model}
            return {"success": False, "content": f"API错误: {resp.status_code}", "tokens": 0}
        except Exception as e:
            return {"success": False, "content": str(e), "tokens": 0}

    def execute_with_tools(self, messages: list, tools: list, user_id: str = None, temperature: float = 0.7, max_tokens: int = 2000, thinking: bool = False) -> dict:
        
        body = {
            "model": self.model or "deepseek-v4-flash",
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if thinking:
            body["thinking"] = {"type": "enabled"}
   
        if user_id:
            body["user_id"] = user_id

        try:
            resp = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return {"success": True, "data": data, "tokens": tokens}
            return {"success": False, "error": f"API错误: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
