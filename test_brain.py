#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_connector import brain_connector
from agent_core.simple_vector import simple_vector

brain = brain_connector
print(f"✅ 大脑连接成功")
print(f"   经验数: {len(brain.brain.get('experiences', []))}")

print(f"\n✅ 向量库连接成功")
print(f"   条目数: {simple_vector.get_stats()['total_documents']}")
