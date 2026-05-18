"""智能配置驱动层 - 统一管理所有配置"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SmartConfig:
    """智能配置单例"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        # 项目根目录（智能检测）
        self.ROOT = Path(os.environ.get('CLAWSJOY_ROOT', Path(__file__).parent.parent))
        
        # 服务端口（支持环境变量覆盖）
        self.PORTS = {
            'gateway': int(os.environ.get('CLAWSJOY_GATEWAY_PORT', 5002)),
            'multi_agent': int(os.environ.get('CLAWSJOY_MULTI_PORT', 5005)),
            'file_service': int(os.environ.get('CLAWSJOY_FILE_PORT', 5003)),
            'doc_generator': int(os.environ.get('CLAWSJOY_DOC_PORT', 5008)),
            'agent_api': int(os.environ.get('CLAWSJOY_AGENT_API_PORT', 5010)),
            'web': int(os.environ.get('CLAWSJOY_WEB_PORT', 5011)),
            'comfyui': int(os.environ.get('CLAWSJOY_COMFYUI_PORT', 8188)),
            'ollama': int(os.environ.get('OLLAMA_PORT', 11434)),
        }
        
        # 服务主机
        self.HOST = os.environ.get('CLAWSJOY_HOST', '0.0.0.0')
        
        # LLM 配置
        self.LLM_ENDPOINT = os.environ.get('OLLAMA_ENDPOINT', 'http://127.0.0.1:11434')
        self.LLM_MODEL = os.environ.get('DEFAULT_LLM_MODEL', 'qwen2.5:7b')
        
        # 路径配置
        self.PATHS = {
            'data': self.ROOT / 'data',
            'logs': self.ROOT / 'logs',
            'output': self.ROOT / 'output',
            'skills': self.ROOT / 'skills',
            'models': self.ROOT / 'models',
        }
        
        # 创建必要目录
        for path in self.PATHS.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def get_port(self, service):
        return self.PORTS.get(service, 5000)
    
    def get_path(self, name):
        return self.PATHS.get(name, self.ROOT)
    
    def get_service_url(self, service):
        return f"http://{self.HOST}:{self.get_port(service)}"

# 全局实例
smart_config = SmartConfig()
