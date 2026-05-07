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
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:3b"

# CORS
CORS_ORIGINS = ["http://localhost:8082", "http://127.0.0.1:8082"]
