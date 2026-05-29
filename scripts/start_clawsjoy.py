
# 自动注册所有 Agent
from core.lib.agent_registry_manager import agent_registry
print("\n📋 注册 Agents...")
agent_registry.discover_agents()
