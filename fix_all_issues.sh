#!/bin/bash
echo "🔧 ClawsJoy v5 全面修复"

# 1. 修复硬编码密钥
echo "1. 修复硬编码密钥..."
sed -i 's/SECRET_KEY = ".*"/SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")/' scripts/user_preference_service.py

# 2. 添加必要的 import
sed -i '1iimport os' scripts/user_preference_service.py

# 3. 修复硬编码路径（使用环境变量）
cat >> .env << 'ENV'
PROJECT_ROOT=/home/flybo/clawsjoy_v5
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENV

# 4. 创建统一配置模块
cat > core/lib/port_config.py << 'PORT'
"""统一端口配置"""
from core.lib.unified_config import unified_config

def get_port(service_name: str, default: int) -> int:
    return unified_config.get(f"services.{service_name}.port", default)

# 预定义端口
GATEWAY_PORT = 5002
USER_PREFERENCE_PORT = 5445
DRIVER_HTTPS_PORT = 5443
DRIVER_PORT = 5013
LLM_PORT = 5012
PORT

# 5. 创建路径配置模块
cat > core/lib/path_config.py << 'PATH'
"""统一路径配置"""
import os
from pathlib import Path

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.parent.parent))
DATA_ROOT = PROJECT_ROOT / "data"
LOGS_ROOT = PROJECT_ROOT / "logs"
BACKUP_ROOT = PROJECT_ROOT / "backups"

def get_db_path(db_name: str) -> Path:
    return DATA_ROOT / f"{db_name}.db"
PATH

# 6. 移除调试代码（可选，谨慎）
echo "6. 清理调试代码..."
# 注释掉 ipdb 断点
find . -name "*.py" -exec sed -i 's/import ipdb/# import ipdb/g' {} \;
find . -name "*.py" -exec sed -i 's/ipdb.set_trace()/# ipdb.set_trace()/g' {} \;

echo "✅ 全面修复完成"
echo "请测试服务: curl http://127.0.0.1:5002/health"
