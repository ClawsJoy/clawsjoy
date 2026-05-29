"""智能适配器 - 配置驱动，支持多模型、流式输出"""

import yaml
import time
import threading
from pathlib import Path
from typing import Dict, Optional, Generator
from core.lib.llm_manager import llm_manager


class SmartAdapter:
    """智能适配器 - 根据任务自动选择模型"""

    def __init__(self):
        self.config = self._load_config()
        self.default_model = self.config.get('default', {}).get('model', 'qwen2.5:3b')
        self.default_provider = self.config.get('default', {}).get('provider', 'ollama')
        self.default_timeout = self.config.get('performance', {}).get('timeout', 60)
        self.task_types = self.config.get('task_types', {})

    def _load_config(self) -> Dict:
        """加载配置"""
        config_paths = [
            "config/skills/smart_adapter.yaml",
            "config/smart_adapter.yaml"
        ]
        for path in config_paths:
            if Path(path).exists():
                with open(path, 'r') as f:
                    return yaml.safe_load(f) or {}
        print("⚠️ smart_adapter.yaml 未找到，使用默认配置")
        return {}

    def detect_task_type(self, text: str) -> str:
        """检测任务类型"""
        text_lower = text.lower()
        for task_type, task_config in self.task_types.items():
            keywords = task_config.get('keywords', [])
            for keyword in keywords:
                if keyword in text_lower:
                    return task_type
        return 'qa'

    def _get_task_config(self, task_type: str) -> Dict:
        """获取任务配置"""
        task_config = self.task_types.get(task_type, {})
        return {
            'model': task_config.get('model', self.default_model),
            'provider': task_config.get('provider', self.default_provider),
            'temperature': task_config.get('temperature', 0.7),
            'max_tokens': task_config.get('max_tokens', 2000),
            'timeout': task_config.get('timeout', self.default_timeout),
            'system_prompt': task_config.get('system_prompt', '')
        }

    def generate(self, prompt: str, auto_select: bool = True, **kwargs) -> str:
        """生成响应（同步）"""
        if auto_select:
            task_type = self.detect_task_type(prompt)
            config = self._get_task_config(task_type)
            model = config['model']
            provider = config['provider']
            temperature = config['temperature']
            max_tokens = config['max_tokens']
            timeout = config['timeout']
        else:
            model = kwargs.get('model', self.default_model)
            provider = kwargs.get('provider', self.default_provider)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            timeout = kwargs.get('timeout', self.default_timeout)
            task_type = 'custom'

        print(f"🤖 选择模型: {provider}/{model} (超时: {timeout}s)")

        try:
            result = llm_manager.generate(
                prompt=prompt,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            return result
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return f"生成失败: {e}"

    def generate_stream(self, prompt: str, auto_select: bool = True, **kwargs) -> Generator:
        """流式生成响应（异步，不阻塞）"""
        if auto_select:
            task_type = self.detect_task_type(prompt)
            config = self._get_task_config(task_type)
            model = config['model']
            provider = config['provider']
            temperature = config['temperature']
            max_tokens = config['max_tokens']
            timeout = config['timeout']
        else:
            model = kwargs.get('model', self.default_model)
            provider = kwargs.get('provider', self.default_provider)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 2000)
            timeout = kwargs.get('timeout', self.default_timeout)

        print(f"🤖 流式生成: {provider}/{model}")

        try:
            for chunk in llm_manager.generate_stream(prompt=prompt, model=model, provider=provider, timeout=timeout):
                yield chunk
        except Exception as e:
            print(f"流式生成错误: {e}")
            yield f"生成失败: {e}"

    def generate_async(self, prompt: str, callback=None, auto_select: bool = True, **kwargs):
        """异步生成（后台线程，不阻塞）"""
        import threading
        
        def _generate():
            result = self.generate(prompt, auto_select, **kwargs)
            if callback:
                callback(result)
            return result
        
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        return thread


# 全局实例
smart_adapter = SmartAdapter()
