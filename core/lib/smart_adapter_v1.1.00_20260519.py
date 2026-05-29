from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
"""智能适配器 - 根据任务类型自动选择最佳模型"""
import re
from core.lib.llm_manager import llm_manager

class SmartAdapter:
    """智能适配器 - 自动判断任务类型并选择模型"""
    
    # 任务类型配置
    TASK_CONFIG = {
        'math': {
            'keywords': ['计算', '加', '减', '乘', '除', '+', '-', '*', '/', '等于', '多少'],
            'model': 'qwen2.5:3b',
            'provider': 'ollama',
            'max_tokens': 100,
            'system_prompt': '只输出数字结果，不要解释'
        },
        'code': {
            'keywords': ['代码', '函数', '写一个', '编程', 'python', '脚本', '算法'],
            'model': unified_config.get('llm.default_model', 'qwen2.5:7b'),
            'provider': 'ollama',
            'max_tokens': 2000,
            'system_prompt': '只输出代码，不要解释'
        },
        'qa': {
            'keywords': ['是什么', '什么是', '意思', '定义', '解释', '介绍'],
            'model': unified_config.get('llm.default_model', 'qwen2.5:7b'),
            'provider': 'ollama',
            'max_tokens': 500,
            'system_prompt': '简短回答'
        },
        'creative': {
            'keywords': ['写一篇', '创作', '生成故事', '文章', '脚本', '文案'],
            'model': unified_config.get('llm.default_model', 'qwen2.5:7b'),
            'provider': 'ollama',
            'max_tokens': 1500,
            'system_prompt': ''
        },
        'analyze': {
            'keywords': ['分析', '总结', '比较', '评估', '评价', '报告'],
            'model': unified_config.get('llm.default_model', 'qwen2.5:7b'),
            'provider': 'ollama',
            'max_tokens': 1000,
            'system_prompt': ''
        }
    }
    
    def __init__(self):
        self.default_model = unified_config.get('llm.default_model', 'qwen2.5:7b')
        self.default_provider = 'ollama'
    
    def detect_task_type(self, prompt: str) -> dict:
        """检测任务类型"""
        prompt_lower = prompt.lower()
        
        for task_type, config in self.TASK_CONFIG.items():
            for keyword in config['keywords']:
                if keyword in prompt_lower:
                    return {
                        'type': task_type,
                        'confidence': 0.9,
                        **config
                    }
        
        return {
            'type': 'general',
            'confidence': 0.5,
            'model': self.default_model,
            'provider': self.default_provider,
            'max_tokens': 1000,
            'system_prompt': ''
        }
    


    def _fallback_retry(self, prompt, max_retries, backoff):
        """重试机制"""
        import time
        for i in range(max_retries):
            try:
                return self._call_llm(prompt)
            except Exception as e:
                if i == max_retries - 1:
                    raise
                time.sleep(backoff * (i + 1))
        return None

    def _fallback_switch_model(self, prompt, target_model):
        """切换模型"""
        original = self.default_model
        self.default_model = target_model
        try:
            result = self._call_llm(prompt)
            self.default_model = original
            return result
        except:
            self.default_model = original
            raise

    def _fallback_cache(self, prompt, ttl):
        """缓存降级"""
        import hashlib
        import json
        from pathlib import Path
        cache_file = Path(f"{get_data_root()}/cache/llm_cache.json")
        cache_file.parent.mkdir(exist_ok=True)
        
        key = hashlib.md5(prompt.encode()).hexdigest()
        if cache_file.exists():
            import json
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            if key in cache:
                import time
                if time.time() - cache[key]['timestamp'] < ttl:
                    return cache[key]['response']
        return None

    def _call_llm(self, prompt):
        """实际调用 LLM"""
        return self.generate(prompt, auto_select=False)

    def generate(self, prompt: str, auto_select: bool = True) -> str:
        """智能生成 - 自动选择最佳模型"""
        if auto_select:
            task = self.detect_task_type(prompt)
            print(f"🔍 任务类型: {task['type']} (置信度: {task['confidence']})")
            print(f"🤖 选择模型: {task['provider']}/{task['model']}")
            
            # 优化 prompt
            optimized = self._optimize_prompt(prompt, task)
            
            return llm_manager.generate(
                optimized,
                provider=task['provider'],
                model=task['model']
            )
        else:
            return llm_manager.generate(prompt)
    
    def _optimize_prompt(self, prompt: str, task: dict) -> str:
        """优化 prompt"""
        system_prompt = task.get('system_prompt', '')
        if system_prompt:
            return f"{system_prompt}: {prompt}"
        return prompt

# 全局实例
smart_adapter = SmartAdapter()

__version__ = "1.1.0"
__version_date__ = "2026-05-19"
__version_author__ = "ClawsJoy"
__changelog__ = "从 config/smart_adapter.yaml 读取配置，支持任务类型、温度、RAG"
