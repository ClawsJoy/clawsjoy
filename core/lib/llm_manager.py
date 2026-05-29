from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""LLM 管理器"""
import requests
from core.lib.config import config

class LLMManager:
    def __init__(self):
        # 创建 Session 复用连接
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5)
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.endpoint = unified_config.get("llm", {}).get("endpoint", "http://localhost:11434")
        self.default_model = unified_config.get("llm", {}).get("default_model", unified_config.get("llm", {}).get("default_model", unified_config.get("llm", {}).get("default_model", unified_config.get("llm.default_model", get_llm_model()))))
        self.providers = {'ollama': {'endpoint': self.endpoint}}

    def generate(self, prompt, model=None, provider=None, system=None):
        """生成回复，支持 system prompt"""
        model = model or self.default_model
        try:
            if system:
                # 使用 chat 端点
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }
                resp = self.session.post(f"{self.endpoint}/api/chat", json=payload, timeout=get_timeout("llm"))
                data = resp.json()
                return data.get('message', {}).get('content', '')
            else:
                # 使用 generate 端点
                payload = {"model": model, "prompt": prompt, "stream": False}
                resp = self.session.post(f"{self.endpoint}/api/generate", json=payload, timeout=get_timeout("llm"))
                data = resp.json()
                return data.get('response', '')
        except Exception as e:
            print(f"LLM调用错误: {e}")
            return ""
llm_manager = LLMManager()
