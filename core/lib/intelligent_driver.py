"""智能驱动 - 配置驱动的动态执行"""

import os
from typing import Dict, Any


class IntelligentDriver:
    """智能驱动类"""

    VERSION = "1.0.0"

    def __init__(self):
        self.config = {}

    def get_ollama_host(self) -> str:
        """获取 Ollama 主机"""
        return os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

    def get_port(self, service: str) -> int:
        """获取服务端口"""
        ports = {
            "ollama": 11434,
            "gateway": 5002,
            "multi_agent": 5005
        }
        return ports.get(service, 5002)


intelligent_driver = IntelligentDriver()
