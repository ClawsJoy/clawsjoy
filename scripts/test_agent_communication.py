#!/usr/bin/env python3
"""Agent 通信测试"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.agent_communication import agent_comm
from lib.service_registry import service_registry

def test_communication():
    print("=" * 60)
    print("Agent 通信测试")
    print("=" * 60)
    
    # 1. 测试消息发送
    print("\n1. 消息发送测试:")
    msg_id = agent_comm.send(
        from_agent="test_sender",
        to_agent="test_receiver",
        payload={"action": "ping", "data": "hello"}
    )
    print(f"   ✅ 消息已发送: {msg_id}")
    
    # 2. 测试消息历史
    print("\n2. 消息历史测试:")
    history = agent_comm.get_messages(limit=5)
    print(f"   ✅ 历史消息数: {len(history)}")
    
    # 3. 测试统计
    print("\n3. 通信统计:")
    stats = agent_comm.get_stats()
    print(f"   ✅ 总消息数: {stats['total_messages']}")
    
    print("\n✅ Agent 通信测试通过")

if __name__ == "__main__":
    test_communication()
