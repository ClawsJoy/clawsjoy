"""常量模块 - 兼容层，实际使用 unified_config"""
from lib.unified_config import config

# 导出常用常量
LLM = config.LLM
SERVICE_URLS = {
    'GATEWAY': f"http://localhost:{config.get_port('gateway')}",
    'FILE_SERVICE': f"http://localhost:{config.get_port('file')}",
    'MULTI_AGENT': f"http://localhost:{config.get_port('multi_agent')}",
    'DOC_GENERATOR': f"http://localhost:{config.get_port('doc')}",
    'AGENT_API': f"http://localhost:{config.get_port('agent_api')}",
}

PORTS = config.PORTS
PATHS = config.PATHS

def get_port(name):
    return config.get_port(name)

def get_path(name):
    return config.get_path(name)
