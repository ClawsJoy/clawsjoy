#!/usr/bin/env python3
"""深度优化脚本 v2 - 修复硬编码和 TODO"""

import os
import re
from pathlib import Path

print("=" * 70)
print("🔧 ClawsJoy v5 深度优化 v2")
print("=" * 70)

# ============================================================
# 1. 修复硬编码 URL 和端口
# ============================================================
print("\n1. 修复硬编码 URL 和端口...")


def fix_hardcoded_urls(file_path: Path) -> int:
    """修复文件中的硬编码 URL"""
    try:
        content = file_path.read_text()
        original = content

        # 替换硬编码的 localhost URL
        content = re.sub(
            r"https?://localhost:(\d+)",
            r'f"http://{{unified_config.get("services.gateway.host", "localhost")}}:\1"',
            content,
        )

        # 替换硬编码端口
        content = re.sub(
            r"port\s*=\s*(\d{4,5})",
            r'port = unified_config.get("services.\\1.port", \1)',
            content,
        )

        if content != original:
            file_path.write_text(content)
            return 1
    except Exception as e:
        print(f"   ⚠️ 处理 {file_path.name} 失败: {e}")
    return 0


# 扫描并修复
fixed_count = 0
for py_file in Path("core").rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    fixed_count += fix_hardcoded_urls(py_file)

print(f"   ✅ 修复了 {fixed_count} 个文件中的硬编码")

# ============================================================
# 2. 生成 TODO 清单
# ============================================================
print("\n2. 生成 TODO 清单...")

todo_list = []
for py_file in Path(".").rglob("*.py"):
    if "__pycache__" in str(py_file) or "tools" in str(py_file):
        continue
    try:
        lines = py_file.read_text().splitlines()
        for i, line in enumerate(lines):
            if re.search(r"#\s*(TODO|FIXME|HACK|XXX):", line, re.IGNORECASE):
                todo_list.append(
                    {"file": str(py_file), "line": i + 1, "content": line.strip()}
                )
    except:
        pass

print(f"   📝 发现 {len(todo_list)} 个 TODO/FIXME")

# 生成 TODO 报告
with open("TODO_report.md", "w") as f:
    f.write("# ClawsJoy v5 TODO 清单\n\n")
    f.write(f"总计: {len(todo_list)} 个待办项\n\n")
    f.write("| 文件 | 行号 | 内容 |\n")
    f.write("|------|------|------|\n")
    for todo in todo_list[:50]:  # 只显示前50个
        f.write(f"| {todo['file']} | {todo['line']} | {todo['content'][:50]} |\n")

print(f"   📄 TODO 报告已生成: TODO_report.md")

# ============================================================
# 3. 创建统一配置常量
# ============================================================
print("\n3. 创建统一配置常量...")

config_constants = '''#!/usr/bin/env python3
"""统一配置常量 - 避免硬编码"""

from core.lib.unified_config import unified_config

# ============================================================
# 服务端口配置
# ============================================================
GATEWAY_PORT = unified_config.get("services.gateway.port", 5002)
USER_PREFERENCE_PORT = unified_config.get("services.user_preference.port", 5445)
DRIVER_PORT = unified_config.get("services.driver.port", 5013)
DRIVER_HTTPS_PORT = unified_config.get("services.driver_https.port", 5443)
LLM_PORT = unified_config.get("services.llm.port", 5012)
WEBSOCKET_PORT = unified_config.get("services.websocket.port", 5003)

# ============================================================
# 服务地址配置
# ============================================================
GATEWAY_HOST = unified_config.get("services.gateway.host", "localhost")
OLLAMA_URL = unified_config.get("llm.ollama_url", "http://localhost:11434")

# ============================================================
# 超时配置
# ============================================================
DEFAULT_TIMEOUT = unified_config.get("timeouts.default", 30)
LONG_TIMEOUT = unified_config.get("timeouts.long", 120)
SHORT_TIMEOUT = unified_config.get("timeouts.short", 5)

# ============================================================
# 数据库配置
# ============================================================
DB_POOL_SIZE = unified_config.get("database.pool_size", 10)
DB_MAX_IDLE_TIME = unified_config.get("database.max_idle_time", 300)

# ============================================================
# 日志配置
# ============================================================
LOG_LEVEL = unified_config.get("logging.level", "INFO")
LOG_FORMAT = unified_config.get("logging.format", 
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
'''

constants_path = Path("core/lib/constants.py")
constants_path.write_text(config_constants)
print(f"   ✅ 已创建: {constants_path}")

# ============================================================
# 4. 优化建议报告
# ============================================================
print("\n4. 生成优化建议报告...")

suggestions = """
# ClawsJoy v5 优化建议报告

## 高优先级 (立即执行)

### 1. 修复硬编码配置
- 将 `config/security/jwt.yaml` 中的密钥移至环境变量
- 使用 `core/lib/constants.py` 统一管理端口和 URL

### 2. 处理 TODO 项
- 优先处理 `aliyun_pai.py` 中的 TODO（阿里云集成）
- 完成 `skill_evolver.py` 中的技能进化逻辑

### 3. 添加数据库连接池
- 已创建 `core/lib/db_pool.py`，需要在各模块中使用

## 中优先级 (本周完成)

### 4. 添加请求追踪
- 集成 OpenTelemetry 或 Jaeger
- 添加请求 ID 到所有日志

### 5. 完善单元测试
- 当前测试覆盖率较低
- 为核心模块添加单元测试

### 6. 优化日志
- 使用结构化日志 (JSON 格式)
- 添加敏感信息脱敏

## 低优先级 (可选)

### 7. 代码重构
- 拆分 `agent_gateway_enhanced.py` (1272 行)
- 统一异常处理

### 8. 性能优化
- 实现请求缓存
- 优化数据库查询
"""

suggestions_path = Path("OPTIMIZATION_REPORT.md")
suggestions_path.write_text(suggestions)
print(f"   📄 优化建议报告: {suggestions_path}")

print("\n" + "=" * 70)
print("✅ 深度优化完成")
print("=" * 70)
