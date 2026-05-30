#!/usr/bin/env python3
"""初始化 Agent 注册（启动时执行一次）"""

import sys
sys.path.insert(0, '.')

from core.lib.agent_registry_manager import agent_registry

def main():
    print("="*50)
    print("初始化 Agent 注册")
    print("="*50)
    
    # 发现并注册所有 Agent
    result = agent_registry.discover_agents()
    print(f"\n✅ 已注册 {len(result)} 个 Agent")
    
    # 列出已注册的 Agent
    agents = agent_registry.list_registered_agents()
    print("\n已注册 Agent 列表:")
    for a in agents:
        print(f"  - {a.get('agent_name')}")

if __name__ == "__main__":
    main()
