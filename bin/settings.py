#!/usr/bin/env python3
"""ClawsJoy 统一配置。

优先读取环境变量，未设置时回退到合理默认值。
"""

import os
from pathlib import Path


def _resolve_root() -> Path:
    env_root = os.getenv("CLAWSJOY_ROOT")
    if env_root:
        return Path(env_root)

    candidates = [Path("/mnt/d/clawsjoy"), Path("/root/clawsjoy")]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    # 最终回退为当前文件上级目录（bin 的父目录）。
    return Path(__file__).resolve().parent.parent


CLAWSJOY_ROOT = _resolve_root()
DATA_DIR = Path(os.getenv("CLAWSJOY_DATA_DIR", str(CLAWSJOY_ROOT / "data")))
TENANTS_DIR = Path(os.getenv("CLAWSJOY_TENANTS_DIR", str(CLAWSJOY_ROOT / "tenants")))
LOGS_DIR = Path(os.getenv("CLAWSJOY_LOGS_DIR", str(CLAWSJOY_ROOT / "logs")))
LOG_APP_DIR = Path(os.getenv("CLAWSJOY_LOG_APP_DIR", str(LOGS_DIR / "app")))
LOG_RUNNER_DIR = Path(os.getenv("CLAWSJOY_LOG_RUNNER_DIR", str(LOGS_DIR / "runner")))
LOG_AUDIT_DIR = Path(os.getenv("CLAWSJOY_LOG_AUDIT_DIR", str(LOGS_DIR / "audit")))
LOG_SYSTEM_DIR = Path(os.getenv("CLAWSJOY_LOG_SYSTEM_DIR", str(LOGS_DIR / "system")))
SKILLS_DIR = Path(
    os.getenv("CLAWSJOY_SKILLS_DIR", str(CLAWSJOY_ROOT / "skills" / "auto_generated"))
)

# 任务队列默认统一为持久化 tenants 路径，可用环境变量覆盖。
TASK_QUEUE_DIR = Path(os.getenv("CLAWSJOY_TASK_QUEUE_DIR", str(TENANTS_DIR / "queue")))

PORT_AUTH = int(os.getenv("CLAWSJOY_PORT_AUTH", "8092"))
PORT_TENANT = int(os.getenv("CLAWSJOY_PORT_TENANT", "8088"))
PORT_BILLING = int(os.getenv("CLAWSJOY_PORT_BILLING", "8090"))
PORT_TASK = int(os.getenv("CLAWSJOY_PORT_TASK", "8084"))
PORT_JOYMATE = int(os.getenv("CLAWSJOY_PORT_JOYMATE", "8080"))
PORT_COFFEE = int(os.getenv("CLAWSJOY_PORT_COFFEE", "8085"))
PORT_PROMO = int(os.getenv("CLAWSJOY_PORT_PROMO", "8086"))
