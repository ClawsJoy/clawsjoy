#!/usr/bin/env python3
"""Llm Client - Llm Client 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests

class LLMClient:
    def __init__(self, model: str = config_helper.get_llm_model(fast=True), url: str = config_helper.get_llm_endpoint()):
        self.model = model
        self.url = f"{url}/api/generate"
    
    def chat(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=config_helper.get_timeout("llm")
            )
            if response.status_code == 200:
                return response.json().get("response", "无响应内容")
        except Exception as e:
            print(f"LLM 调用错误: {e}")
        return "抱歉，我暂时无法回答这个问题。"
