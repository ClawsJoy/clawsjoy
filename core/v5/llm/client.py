#!/usr/bin/env python3
"""LLM Client - LLM 客户端模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import time
from pathlib import Path
from typing import Dict, Optional

import requests
import yaml

from core.lib import config_helper


class LLMClient:
    """LLM 客户端"""

    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config.get("base_url", config_helper.get_llm_endpoint())
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)

        # 模型配置
        models = self.config.get("models", {})
        self.default_model = models.get("default", "qwen2.5:3b")
        self.chat_model = models.get("chat", {}).get("model", self.default_model)
        self.decision_model = models.get("decision", {}).get(
            "model", self.default_model
        )
        self.code_model = models.get("code", {}).get("model", self.default_model)

    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "llm.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _make_request(
        self, endpoint: str, payload: Dict, retry: int = 0
    ) -> Optional[Dict]:
        """发送请求"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", json=payload, timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            if retry < self.max_retries:
                time.sleep(2**retry)
                return self._make_request(endpoint, payload, retry + 1)
        return None

    def chat(
        self, message: str, model: str = None, system_prompt: str = None
    ) -> Optional[str]:
        """聊天"""
        model = model or self.chat_model
        payload = {"model": model, "messages": []}
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        payload["messages"].append({"role": "user", "content": message})
        payload["stream"] = False

        result = self._make_request("/api/chat", payload)
        if result:
            return result.get("message", {}).get("content", "")
        return None

    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """生成响应"""
        model = model or self.default_model
        payload = {"model": model, "prompt": prompt, "stream": False}
        result = self._make_request("/api/generate", payload)
        if result:
            return result.get("response", "")
        return None


# 全局实例
llm = LLMClient()
