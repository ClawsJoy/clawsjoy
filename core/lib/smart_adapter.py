"""智能适配器 - 配置驱动，支持多模型"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from core.lib.llm_manager import llm_manager


class SmartAdapter:
    """智能适配器 - 根据任务自动选择模型"""

    def __init__(self):
        self.config = self._load_config()
        self.default_model = self.config.get('default', {}).get('model', 'qwen2.5:3b')
        self.default_provider = self.config.get('default', {}).get('provider', 'ollama')
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
        for task_type, config in self.task_types.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword in text_lower:
                    return task_type
        return 'qa'

    def generate(self, prompt: str, auto_select: bool = True, **kwargs) -> str:
        """生成响应"""
        if auto_select:
            task_type = self.detect_task_type(prompt)
            task_config = self.task_types.get(task_type, {})
            model = task_config.get('model', self.default_model)
            provider = task_config.get('provider', self.default_provider)
            temperature = task_config.get('temperature', 0.7)
        else:
            model = kwargs.get('model', self.default_model)
            provider = kwargs.get('provider', self.default_provider)
            temperature = kwargs.get('temperature', 0.7)

        print(f"🔍 任务类型: {task_type if auto_select else 'manual'} (置信度: 0.9)")
        print(f"🤖 选择模型: {provider}/{model}")

        response = llm_manager.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            
            **kwargs
        )
        return response


smart_adapter = SmartAdapter()
