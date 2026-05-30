#!/usr/bin/env python3
#!/usr/bin/env python3
"""Clawsjoy Simple - Clawsjoy Simple 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
import re
from pathlib import Path; import sys; sys.path.insert(0, str(Path(__file__).parent))


class SimpleClawsJoy:
    VERSION = "5.0.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.name = None
        self.preferences = []
        print(f"🦞 ClawsJoy v{self.VERSION} 启动")
        print(f"👤 用户: {user_id}")
    
    def process(self, user_input: str) -> str:
        lower = user_input.lower()
        
        # 自我介绍
        if re.match(r'^[我][叫][\s]*([^\s，。]{2,4})$', user_input.strip()):
            match = re.search(r'叫[\s]*([^\s，。]{2,4})', user_input)
            if match:
                self.name = match.group(1)
                return f"你好，{self.name}！我是 ClawsJoy 智能助手"
        
        # 问候
        if any(g in lower for g in ['你好', 'hi']):
            if self.name:
                return f"你好，{self.name}！我是 ClawsJoy，有什么可以帮你的？"
            return "你好！我是 ClawsJoy 智能助手，请问怎么称呼你？"
        
        # 问名字
        if any(q in lower for q in ['我叫什么', '我名字', '还记得我吗']):
            if self.name:
                return f"当然记得！你是{self.name}呀"
            return "我是 ClawsJoy，你还没告诉我名字呢"
        
        # Agent 列表
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            return "我是 ClawsJoy。系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent"
        
        # 你是谁
        if '你是谁' in lower or '你叫什么' in lower:
            return "我是 ClawsJoy，你的智能助手！"
        
        # 默认
        return f"我是 ClawsJoy。收到：{user_input[:50]}"
    
    def chat(self, user_input: str) -> str:
        return self.process(user_input)
    
    def interactive_mode(self):
        print("\n" + "=" * 50)
        print("ClawsJoy 交互模式 (输入 'exit' 退出)")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 再见！")
                    break
                if not user_input:
                    continue
                
                response = self.chat(user_input)
                print(f"🤖 {response}")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", default="default")
    parser.add_argument("-m", "--message")
    parser.add_argument("-i", "--interactive", action="store_true")
    args = parser.parse_args()
    
    claws = SimpleClawsJoy(args.user)
    
    if args.message:
        print(f"🤖 {claws.chat(args.message)}")
    else:
        claws.interactive_mode()
