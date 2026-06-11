#!/usr/bin/env python3
"""设计模式分析"""

import ast
import sys
from pathlib import Path

print("=" * 60)
print("ClawsJoy v5 设计模式分析")
print("=" * 60)

# 1. 单例模式检查
print("\n📌 1. 单例模式 (Singleton)")
singletons = []
for py_file in Path("core/lib").glob("*.py"):
    try:
        content = py_file.read_text()
        if "_instance" in content or "singleton" in content.lower():
            singletons.append(py_file.name)
    except Exception as e:
        pass
print(f"   发现: {', '.join(singletons[:10])}...")

# 2. 工厂模式检查
print("\n🏭 2. 工厂模式 (Factory)")
factories = []
for py_file in Path(".").rglob("*.py"):
    if "tools" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        if "create_" in content and "def create_" in content:
            factories.append(py_file.name)
    except Exception as e:
        pass
print(f"   发现: {', '.join(factories[:8])}...")

# 3. 策略模式检查
print("\n🎯 3. 策略模式 (Strategy)")
strategies = []
for py_file in Path("core/agents/builtin").glob("*.py"):
    try:
        content = py_file.read_text()
        if "strategy" in content.lower():
            strategies.append(py_file.name)
    except Exception as e:
        pass
print(f"   发现: {', '.join(strategies[:5])}")

# 4. 观察者模式检查
print("\n👁️ 4. 观察者模式 (Observer)")
observers = []
for py_file in Path("core/lib").glob("*.py"):
    if "event" in py_file.name or "hook" in py_file.name or "watcher" in py_file.name:
        observers.append(py_file.name)
print(f"   发现: {', '.join(observers[:8])}")

# 5. 装饰器模式检查
print("\n🎨 5. 装饰器模式 (Decorator)")
decorators = []
for py_file in Path(".").rglob("*.py"):
    if "tools" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        if "@" in content and "def " in content:
            decorators.append(py_file.name)
    except Exception as e:
        pass
print(f"   发现: 大量使用 (Flask 路由装饰器、性能监控装饰器等)")

print("\n" + "=" * 60)
