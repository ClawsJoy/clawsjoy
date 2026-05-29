#!/usr/bin/env python3
"""ClawsJoy 5.4 统一入口"""

import sys
import argparse
sys.path.insert(0, '.')

from core.agents.builtin.life_cycle_enhanced import LifeCycleEnhanced


class ClawsJoy:
    VERSION = "5.4.0"
    
    def __init__(self, user_id: str = "default"):
        self.agent = LifeCycleEnhanced(user_id)
        print(f"🦞 ClawsJoy v{self.VERSION} 启动")
    
    def chat(self, user_input: str) -> str:
        return self.agent.process(user_input)['response']
    
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
    parser = argparse.ArgumentParser(description="ClawsJoy 5.4")
    parser.add_argument("-u", "--user", default="default", help="用户ID")
    parser.add_argument("-m", "--message", help="直接发送消息")
    parser.add_argument("-i", "--interactive", action="store_true", help="交互模式")
    
    args = parser.parse_args()
    
    claws = ClawsJoy(args.user)
    
    if args.message:
        print(f"🤖 {claws.chat(args.message)}")
    elif args.interactive:
        claws.interactive_mode()
    else:
        # 默认进入交互模式
        claws.interactive_mode()
