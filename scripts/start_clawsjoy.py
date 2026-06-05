#!/usr/bin/env python3
"""Start Clawsjoy - Start Clawsjoy 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


# 自动注册所有 Agent
from core.lib.agent_registry_manager import agent_registry

print("\n📋 注册 Agents...")
agent_registry.discover_agents()
