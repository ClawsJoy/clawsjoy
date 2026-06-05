#!/usr/bin/env python3
"""修复后的 Agent 协作与通信验证"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🔗 Agent 协作与通信验证 (修复版)")
print("=" * 60)

# 1. Agent 注册表测试
print("\n1. Agent 注册表测试...")
from core.lib.agent_registry import agent_registry

stats = agent_registry.get_stats()
print(f"   📊 已注册 Agent: {stats.get('total', 0)}")
print(f"   ✅ 活跃 Agent: {stats.get('active', 0)}")
print(f"   📋 Agent 列表: {stats.get('agents', [])}")

# 列出所有 Agent
all_agents = agent_registry.list_all()
print(f"   📝 list_all() 返回 {len(all_agents)} 个 Agent")
if all_agents:
    print(f"      示例: {list(all_agents.keys())[:5]}")

# 获取特定 Agent
chat_agent = agent_registry.get("chat_agent")
if chat_agent:
    print(f"   💬 chat_agent: {chat_agent.get('description', 'N/A')[:50]}")

# 2. Agent 通信总线测试
print("\n2. Agent 通信总线测试...")
from core.lib.agent_bus import AgentBus

bus = AgentBus()
print(f"   ✅ AgentBus 加载成功")

# 测试发布/订阅
received_messages = []


def test_handler(message):
    received_messages.append(message)
    print(f"   📨 收到消息: {message.get('data', message)}")


bus.subscribe("test_topic", test_handler)
bus.publish("test_topic", {"data": "Hello, ClawsJoy!"})
print(f"   ✅ 发布/订阅测试完成 (收到 {len(received_messages)} 条消息)")

# 获取总线状态
status = bus.get_status()
print(f"   📊 总线状态: {status}")

# 3. 工作区管理器测试
print("\n3. 工作区管理器测试...")
try:
    from agents.workspace_manager import workspace_manager

    if hasattr(workspace_manager, "list_workspaces"):
        workspaces = workspace_manager.list_workspaces()
        print(f"   📁 工作区数量: {len(workspaces)}")
        for ws in workspaces[:3]:
            print(f"      - {ws.get('name', ws) if isinstance(ws, dict) else ws}")
    else:
        print(
            f"   📋 workspace_manager 可用方法: {[m for m in dir(workspace_manager) if not m.startswith('_')][:5]}"
        )
except ImportError as e:
    print(f"   ⚠️ 工作区管理器导入: {e}")
    # 尝试其他位置
    try:
        from core.workspace.manager import workspace_manager

        print(f"   ✅ 从 core.workspace 加载成功")
    except ImportError:
        print("   ⚠️ 工作区管理器未找到")

print("\n✅ Agent 协作测试完成")
