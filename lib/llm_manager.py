"""多模型管理器 - 支持多种 LLM 后端"""
import requests
import json
from typing import Dict, List, Optional

class LLMManager:
    """多模型管理器"""
    
    SUPPORTED_PROVIDERS = ['ollama', 'openai', 'local']
    
    def __init__(self, config_path="config/llm_config.yaml"):
        self.config = self._load_config(config_path)
        self._current_provider = self.config.get('default_provider', 'ollama')
    
    def _load_config(self, path):
        import yaml
        from pathlib import Path
        if Path(path).exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'default_provider': 'ollama',
            'providers': {
                'ollama': {'endpoint': 'http://127.0.0.1:11434', 'model': 'qwen2.5:7b'},
                'openai': {'model': 'gpt-3.5-turbo', 'api_key': ''},
                'local': {'endpoint': 'http://127.0.0.1:8000', 'model': 'local'}
            }
        }
    
    def generate(self, prompt: str, provider: str = None, **kwargs) -> str:
        """生成响应"""
        provider = provider or self._current_provider
        
        if provider == 'ollama':
            return self._ollama_generate(prompt, **kwargs)
        elif provider == 'openai':
            return self._openai_generate(prompt, **kwargs)
        else:
            return self._local_generate(prompt, **kwargs)
    
    def _ollama_generate(self, prompt: str, model: str = None, timeout: int = 60) -> str:
        """Ollama 生成"""
        config = self.config['providers']['ollama']
        endpoint = config['endpoint']
        model = model or config.get('model', 'qwen2.5:7b')
        
        try:
            resp = requests.post(
                f"{endpoint}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout
            )
            return resp.json().get('response', '')
        except Exception as e:
            return f"Ollama 错误: {e}"
    
    def _openai_generate(self, prompt: str, model: str = None) -> str:
        """OpenAI 生成"""
        import openai
        config = self.config['providers']['openai']
        api_key = config.get('api_key')
        if not api_key:
            return "请配置 OPENAI_API_KEY"
        
        openai.api_key = api_key
        model = model or config.get('model', 'gpt-3.5-turbo')
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI 错误: {e}"
    
    def _local_generate(self, prompt: str, endpoint: str = None) -> str:
        """本地模型生成"""
        config = self.config['providers']['local']
        endpoint = endpoint or config.get('endpoint', 'http://127.0.0.1:8000')
        
        try:
            resp = requests.post(
                f"{endpoint}/generate",
                json={"prompt": prompt},
                timeout=60
            )
            return resp.json().get('response', '')
        except Exception as e:
            return f"本地模型错误: {e}"
    
    def list_models(self, provider: str = None) -> List[str]:
        """列出可用模型"""
        if provider == 'ollama':
            try:
                resp = requests.get(f"{self.config['providers']['ollama']['endpoint']}/api/tags")
                models = resp.json().get('models', [])
                return [m['name'] for m in models]
            except:
                return ['qwen2.5:7b', 'qwen2.5:3b', 'llama3.2:3b']
        return list(self.config['providers'].keys())
    
    def switch_provider(self, provider: str):
        """切换默认提供商"""
        if provider in self.SUPPORTED_PROVIDERS:
            self._current_provider = provider
            return True
        return False

# 全局实例
llm_manager = LLMManager()
