import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from agents.code_agent.agent_v4 import CodeAgentV4
import json

agent = CodeAgentV4('cross_final')

# 模拟 chat_agent 记住名字后的记忆查询
# 先通过 memory 直接记住
from core.lib.v25_unified_bridge import v25_bridge
v25_bridge.remember('cross_final', '名字', '王小明')

# 然后测试 code_agent 能否查询
result = agent.process('我叫什么名字', {'memories': [{'content': '名字: 王小明'}]})
print(f'result: {result}')
