#!/usr/bin/env python3
"""测试 Agent 间通信"""

import sys
sys.path.insert(0, '{ROOT}')

from lib.agent_communication import agent_comm, MessageType
from agents.orchestrator import orchestrator
from agents.video_agent import video_agent
from agents.memory_manager import memory_manager

print("=" * 50)
print("Agent 间通信测试")
print("=" * 50)

# 1. 订阅事件
memory_manager.subscribe_to("video_created")
print("✅ memory_manager 订阅了 video_created 事件")

# 2. orchestrator 发送请求给 video_agent
print("\n📨 orchestrator 请求 video_agent 制作视频...")
msg_id = agent_comm.send(
    from_agent="orchestrator",
    to_agent="video_agent",
    payload={"action": "make_video", "topic": "香港高才通"},
    msg_type=MessageType.REQUEST
)

# 3. video_agent 响应
print("\n📨 video_agent 响应...")
agent_comm.respond(msg_id, {"result": "视频已生成", "video_path": "output/test.mp4"})

# 4. 广播事件
print("\n📢 orchestrator 广播 video_created 事件...")
agent_comm.send_broadcast(
    from_agent="orchestrator",
    event_type="video_created",
    payload={"video_id": "test_001", "topic": "香港高才通"}
)

# 5. 查看消息历史
print("\n📋 消息历史:")
messages = agent_comm.get_messages(limit=10)
for m in messages:
    print(f"  {m['from']} -> {m['to']}: {m['type']}")

# 6. 查看统计
print(f"\n📊 通信统计: {agent_comm.get_stats()}")

print("\n✅ Agent 通信测试完成")
