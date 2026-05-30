#!/usr/bin/env python3
"""Client - Client 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests
import time
import yaml
from pathlib import Path
from typing import Dict, Optional


class LLMClient:
    """LLM 客户端"""
    
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config.get('base_url', config_helper.get_llm_endpoint())
        self.timeout = self.config.get('timeout', 60)
        self.max_retries = self.config.get('max_retries', 3)

        # 模型配置
        models = self.config.get('models', {})
        self.default_model = models.get('default', 'qwen2.5:3b')
        self.chat_model = models.get('chat', {}).get('model', self.default_model)
        self.decision_model = models.get('decision', {}).get('model', self.default_model)
        self.code_model = models.get('code', {}).get('model', self.default_model)

        # 温度配置
        self.chat_temp = models.get('chat', {}).get('temperature', 0.7)
        self.decision_temp = models.get('decision', {}).get('temperature', 0.3)
        self.code_temp = models.get('code', {}).get('temperature', 0.2)
    
    def _load_config(self) -> Dict:
        config_file = Path("config/v5/llm.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            "base_url": config_helper.get_llm_endpoint(),
            "timeout": 60,
            "max_retries": 3,
            "models": {
                "default": config_helper.get_llm_model(fast=True),
                "chat": {"model": config_helper.get_llm_model(fast=True), "temperature": 0.7},
                "decision": {"model": config_helper.get_llm_model(fast=True), "temperature": 0.3},
                "code": {"model": "deepseek-coder:6.7b", "temperature": 0.2}
            }
        }
    
    def generate(self, prompt: str, model_type: str = "default", temperature: float = None) -> str:
        """生成响应"""
        if model_type == "chat":
            model = self.chat_model
            temp = temperature if temperature is not None else self.chat_temp
        elif model_type == "decision":
            model = self.decision_model
            temp = temperature if temperature is not None else self.decision_temp
        elif model_type == "code":
            model = self.code_model
            temp = temperature if temperature is not None else self.code_temp
        else:
            model = self.default_model
            temp = temperature if temperature is not None else 0.7

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": temp}
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json().get('response', '')
                
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)

        return "抱歉，服务暂时不可用，请稍后重试"


llm = LLMClient()
