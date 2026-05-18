"""LLM 管理器"""
import requests
from lib.config import config

class LLMManager:
    def __init__(self):
        self.endpoint = config.get("llm.endpoint", "http://127.0.0.1:11434")
        self.default_model = config.get("llm.default_model", "qwen2.5:7b")
        self.providers = {'ollama': {'endpoint': self.endpoint}}

    def generate(self, prompt, model=None):
        model = model or self.default_model
        try:
            resp = requests.post(
                f"{self.endpoint}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60
            )
            return resp.json().get('response', '')
        except Exception as e:
            return f"LLM调用失败: {e}"

llm_manager = LLMManager()
