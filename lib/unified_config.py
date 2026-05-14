"""统一配置加载器 - 所有模块从这里读取配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class UnifiedConfig:
    """统一配置单例"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        # 项目根目录
        self.ROOT = Path(os.environ.get('CLAWSJOY_ROOT', '/mnt/d/clawsjoy'))
        
        # 端口配置
        self.PORTS = {
            'gateway': int(os.environ.get('CLAWSJOY_GATEWAY_PORT', 5002)),
            'file': int(os.environ.get('CLAWSJOY_FILE_PORT', 5003)),
            'multi_agent': int(os.environ.get('CLAWSJOY_MULTI_PORT', 5005)),
            'doc': int(os.environ.get('CLAWSJOY_DOC_PORT', 5008)),
            'agent_api': int(os.environ.get('CLAWSJOY_AGENT_API_PORT', 5010)),
            'web': int(os.environ.get('CLAWSJOY_WEB_PORT', 5011)),
            'ollama': int(os.environ.get('OLLAMA_PORT', 11434)),
        }
        
        # LLM 配置
        self.LLM = {
            'ollama_endpoint': os.environ.get('OLLAMA_HOST', 'http://127.0.0.1:11434'),
            'default_model': os.environ.get('CLAWSJOY_DEFAULT_MODEL', 'qwen2.5:7b'),
            'fast_model': os.environ.get('CLAWSJOY_FAST_MODEL', 'qwen2.5:3b'),
            'timeout': int(os.environ.get('CLAWSJOY_LLM_TIMEOUT', 60)),
            'max_retries': int(os.environ.get('CLAWSJOY_LLM_RETRIES', 3)),
        }
        
        # 路径配置
        self.PATHS = {
            'data': self.ROOT / 'data',
            'logs': self.ROOT / 'logs',
            'output': self.ROOT / 'output',
            'skills': self.ROOT / 'skills',
            'agents': self.ROOT / 'agents',
            'config': self.ROOT / 'config',
            'uploads': self.ROOT / 'data/uploads',
            'bg': self.ROOT / 'output/bg',
            'characters': self.ROOT / 'output/characters',
            'knowledge': self.ROOT / 'data/knowledge',
            'tenants': self.ROOT / 'tenants',
        }
        
        # 创建必要目录
        for path in self.PATHS.values():
            if path.suffix == '':
                path.mkdir(parents=True, exist_ok=True)
    
    def get_port(self, name):
        return self.PORTS.get(name, 5000)
    
    def get_path(self, name):
        return self.PATHS.get(name, self.ROOT / name)
    
    def get_llm(self, key):
        return self.LLM.get(key)

# 全局实例
config = UnifiedConfig()
