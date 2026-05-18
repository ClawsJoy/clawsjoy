#!/usr/bin/env python3
"""聊天 Agent"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from lib.file_exchange import file_exchange
from lib.config_loader import config

print("✅ 聊天 Agent 启动")

# 简单实现
class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__("ChatAgent")
    
    def process(self, user_input, context=None):
        return {"response": f"收到: {user_input}"}

if __name__ == "__main__":
    agent = ChatAgent()
    print("聊天 Agent 运行中...")
    while True:
        import time
        time.sleep(1)
