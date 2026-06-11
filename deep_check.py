#!/usr/bin/env python3
"""ClawsJoy v5 深度检查脚本"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 70)
print("🔬 ClawsJoy v5 深度检查报告")
print("=" * 70)

# ============================================================
# 1. 性能分析
# ============================================================
print("\n" + "=" * 50)
print("📊 1. 性能分析")
print("=" * 50)

# CPU 和内存
try:
    import psutil

    print(f"   CPU 使用率: {psutil.cpu_percent(interval=1)}%")
    print(f"   内存使用: {psutil.virtual_memory().percent}%")
    print(f"   可用内存: {psutil.virtual_memory().available / 1024**3:.1f} GB")
except Exception as e:
    print("   ⚠️ psutil 不可用")

# 进程信息
result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
gunicorn_procs = [
    l for l in result.stdout.split("\n") if "gunicorn" in l and "grep" not in l
]
print(f"   Gunicorn 进程数: {len(gunicorn_procs)}")
for proc in gunicorn_procs[:3]:
    parts = proc.split()
    if len(parts) >= 4:
        print(f"      PID: {parts[1]}, CPU: {parts[2]}%, MEM: {parts[3]}%")

# ============================================================
# 2. 数据库分析
# ============================================================
print("\n" + "=" * 50)
print("🗄️ 2. 数据库分析")
print("=" * 50)

db_files = list(Path("data").glob("*.db"))
print(f"   数据库文件数: {len(db_files)}")
total_size = sum(f.stat().st_size for f in db_files) / 1024
print(f"   总大小: {total_size:.1f} KB")

# 检查最大的数据库
if db_files:
    largest = max(db_files, key=lambda f: f.stat().st_size)
    print(f"   最大数据库: {largest.name} ({largest.stat().st_size / 1024:.1f} KB)")

# 检查是否有数据库索引
for db_file in db_files[:3]:
    try:
        import sqlite3

        conn = sqlite3.connect(db_file)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        print(f"   {db_file.name}: {len(indexes)} 个索引")
        conn.close()
    except Exception as e:
        pass

# ============================================================
# 3. 代码复杂度分析
# ============================================================
print("\n" + "=" * 50)
print("📝 3. 代码复杂度分析")
print("=" * 50)

# 统计 Python 文件
py_files = list(Path(".").rglob("*.py"))
py_files = [
    f for f in py_files if "__pycache__" not in str(f) and "tools" not in str(f)
]
print(f"   Python 文件数: {len(py_files)}")

# 统计代码行数
total_lines = 0
large_files = []
for f in py_files[:500]:  # 限制数量
    try:
        lines = len(f.read_text().splitlines())
        total_lines += lines
        if lines > 1000:
            large_files.append((f.name, lines))
    except Exception as e:
        pass
print(f"   代码行数 (抽样): ~{total_lines}")

if large_files:
    print(f"   大文件 (>1000行): {len(large_files)}")
    for name, lines in large_files[:5]:
        print(f"      {name}: {lines} 行")

# ============================================================
# 4. 依赖安全检查
# ============================================================
print("\n" + "=" * 50)
print("🔐 4. 依赖安全检查")
print("=" * 50)

# 检查过时包
try:
    result = subprocess.run(
        ["pip", "list", "--outdated"], capture_output=True, text=True
    )
    outdated = [l for l in result.stdout.split("\n") if "----" not in l and l.strip()]
    print(f"   过时包数量: {len(outdated) - 1}")
    for pkg in outdated[1:6]:  # 显示前5个
        print(f"      {pkg[:60]}")
except Exception as e:
    print("   ⚠️ 无法检查过时包")

# ============================================================
# 5. 日志分析
# ============================================================
print("\n" + "=" * 50)
print("📋 5. 日志分析")
print("=" * 50)

log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
print(f"   日志文件数: {len(log_files)}")
total_log_size = sum(f.stat().st_size for f in log_files) / 1024
print(f"   日志总大小: {total_log_size:.1f} KB")

# 检查错误日志
error_log = Path("logs/error.log")
if error_log.exists():
    with open(error_log) as f:
        lines = f.readlines()
        errors = [l for l in lines if "ERROR" in l]
        print(f"   错误日志条目: {len(errors)}")
        if errors:
            print(f"   最新错误: {errors[-1][:100]}")

# ============================================================
# 6. 配置完整性
# ============================================================
print("\n" + "=" * 50)
print("⚙️ 6. 配置完整性")
print("=" * 50)

config_files = list(Path("config").rglob("*.yaml"))
print(f"   配置文件数: {len(config_files)}")

# 检查环境变量
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        env_vars = [l for l in f.read().splitlines() if l and not l.startswith("#")]
    print(f"   环境变量数: {len(env_vars)}")
    for var in env_vars[:5]:
        print(f"      {var[:40]}")

# ============================================================
# 7. 测试覆盖率
# ============================================================
print("\n" + "=" * 50)
print("🧪 7. 测试覆盖率")
print("=" * 50)

test_files = list(Path("tests").glob("test_*.py")) if Path("tests").exists() else []
print(f"   测试文件数: {len(test_files)}")

# 检查是否有 pytest 配置
if Path("pytest.ini").exists():
    print("   ✅ pytest 已配置")
else:
    print("   ⚠️ pytest 未配置")

# ============================================================
# 8. 安全建议
# ============================================================
print("\n" + "=" * 50)
print("🛡️ 8. 安全建议")
print("=" * 50)

# 检查敏感文件权限
sensitive_files = [".env", "config/security/jwt.yaml"]
for f in sensitive_files:
    path = Path(f)
    if path.exists():
        mode = oct(path.stat().st_mode)[-3:]
        print(f"   {f}: 权限 {mode}")
        if mode != "600":
            print(f"      ⚠️ 建议改为 600")

# 检查调试模式
gunicorn_conf = Path("gunicorn.conf.py")
if gunicorn_conf.exists():
    content = gunicorn_conf.read_text()
    if "debug=True" in content:
        print("   ⚠️ 调试模式已开启，生产环境建议关闭")

print("\n" + "=" * 70)
print("✅ 深度检查完成")
print("=" * 70)
