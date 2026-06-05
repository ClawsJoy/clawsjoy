#!/usr/bin/env python3
"""Agent 协作与通信深度测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🔗 Agent 协作与通信验证")
print("=" * 60)

# 1. Agent 注册表测试
print("\n1. Agent 注册表测试...")
try:
    from core.lib.agent_registry import agent_registry

    stats = agent_registry.get_stats()
    print(f"   📊 已注册 Agent: {stats.get('total', 0)}")
    print(f"   ✅ 活跃 Agent: {stats.get('active', 0)}")

    agents = agent_registry.list_agents()
    for agent in agents[:5]:
        print(
            f"      - {agent.get('name', 'unknown')}: {agent.get('description', '')[:40]}"
        )
except Exception as e:
    print(f"   ⚠️ Agent 注册表: {e}")

# 2. Agent 通信总线测试
print("\n2. Agent 通信总线测试...")
try:
    from core.lib.agent_bus import agent_bus

    # 发送消息
    result = agent_bus.send(to="chat_agent", message="你好", from_="test_system")
    print(f"   📨 发送消息: {result}")

    # 广播消息
    broadcast = agent_bus.broadcast("系统通知: 测试消息")
    print(f"   📢 广播结果: {broadcast}")

except Exception as e:
    print(f"   ⚠️ Agent 总线: {e}")

# 3. 工作区管理器测试
print("\n3. 工作区管理器测试...")
try:
    from core.workspace.manager import workspace_manager

    workspaces = workspace_manager.list_workspaces()
    print(f"   📁 工作区数量: {len(workspaces)}")
    for ws in workspaces[:5]:
        print(f"      - {ws.get('name', 'unknown')}")
except Exception as e:
    print(f"   ⚠️ 工作区管理器: {e}")
