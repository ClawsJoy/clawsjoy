"""智能适配器 - 根据任务类型自动选择最佳模型"""
import re
from lib.llm_manager import llm_manager

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
            'model': 'qwen2.5:7b',
            'provider': 'ollama',
            'max_tokens': 2000,
            'system_prompt': '只输出代码，不要解释'
        },
        'qa': {
            'keywords': ['是什么', '什么是', '意思', '定义', '解释', '介绍'],
            'model': 'qwen2.5:7b',
            'provider': 'ollama',
            'max_tokens': 500,
            'system_prompt': '简短回答'
        },
        'creative': {
            'keywords': ['写一篇', '创作', '生成故事', '文章', '脚本', '文案'],
            'model': 'qwen2.5:7b',
            'provider': 'ollama',
            'max_tokens': 1500,
            'system_prompt': ''
        },
        'analyze': {
            'keywords': ['分析', '总结', '比较', '评估', '评价', '报告'],
            'model': 'qwen2.5:7b',
            'provider': 'ollama',
            'max_tokens': 1000,
            'system_prompt': ''
        }
    }
    
    def __init__(self):
        self.default_model = 'qwen2.5:7b'
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
