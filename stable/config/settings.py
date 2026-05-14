"""ClawsJoy 系统配置"""

import os
from pathlib import Path

# ========== 路径配置 ==========
BASE_DIR = Path("/mnt/d/clawsjoy")
STABLE_DIR = BASE_DIR / "stable"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TENANTS_DIR = BASE_DIR / "tenants"
WEB_DIR = BASE_DIR / "web"

# ========== 服务端口 ==========
PORT_AUTH = 8092
PORT_TENANT = 8088
PORT_BILLING = 8090
PORT_TASK = 8084
PORT_WEB = 8082

# ========== AI 配置 ==========
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:3b"

# ========== Redis 配置 ==========
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# ========== 日志配置 ==========
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "clawsjoy.log"
