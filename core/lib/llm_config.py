"""LLM 统一配置 v4.0.0"""

from lib.config_loader import config

class LLMConfig:
    """LLM 统一配置"""
    
    @staticmethod
    def get_ollama_url() -> str:
        """获取 Ollama URL"""
        host = config.get('services.host', '127.0.0.1')
        port = config.get('services.ports.ollama', 11434)
        return f"http://{host}:{port}/api/generate"
    
    @staticmethod
    def get_ollama_model() -> str:
        """获取默认模型"""
        return config.get('llm.default_model', 'qwen2.5:7b')
    
    @staticmethod
    def get_endpoint() -> str:
        """获取 API 端点"""
        return config.get('llm.endpoint', 'http://127.0.0.1:11434')

llm_config = LLMConfig()

if __name__ == "__main__":
    print(f"Ollama URL: {llm_config.get_ollama_url()}")
