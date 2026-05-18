from lib.smart_config import smart_config
"""ClawsJoy 配置"""

import os
from pathlib import Path

# 基础路径
CLAWSJOY_ROOT = Path("/home/flybo/clawsjoy")
TENANTS_ROOT = CLAWSJOY_ROOT / "tenants"
DATA_ROOT = CLAWSJOY_ROOT / "data"
WEB_ROOT = CLAWSJOY_ROOT / "web"

# 服务端口
PORT_TASK_API = 8084
PORT_WEB = 8082
PORT_AUTH = 8092
PORT_TENANT = 8088

# AI 配置
OLLAMA_URL = "http://smart_config.HOST:str(smart_config.get_port("ollama"))"
OLLAMA_MODEL = "qwen2.5:3b"

# CORS
CORS_ORIGINS = ["http://smart_config.HOST:8082", "http://smart_config.HOST:8082"]
