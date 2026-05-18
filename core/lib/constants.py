from lib.smart_config import smart_config
"""常量模块 - 兼容层，实际使用 unified_config"""
from lib.unified_config import config

# 导出常用常量
LLM = config.LLM
SERVICE_URLS = {
    'GATEWAY': ff"{smart_config.get_service_url("{config.get_port('gateway')}",
    'FILE_SERVICE': ff"{smart_config.get_service_url("{config.get_port('file')}",
    'MULTI_AGENT': ff"{smart_config.get_service_url("{config.get_port('multi_agent')}",
    'DOC_GENERATOR': ff"{smart_config.get_service_url("{config.get_port('doc')}",
    'AGENT_API': ff"{smart_config.get_service_url("{config.get_port('agent_api')}",
}

PORTS = config.PORTS
PATHS = config.PATHS

def get_port(name):
    return config.get_port(name)

def get_path(name):
    return config.get_path(name)
