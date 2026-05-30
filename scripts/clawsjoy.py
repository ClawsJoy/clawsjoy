#!/usr/bin/env python3
#!/usr/bin/env python3
"""Clawsjoy - Clawsjoy 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
from pathlib import Path; import sys; sys.path.insert(0, str(Path(__file__).parent))

from core.agents.builtin.life_cycle_config_driven import LifeCycleConfigDriven


class ClawsJoy:
    VERSION = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.agent = LifeCycleConfigDriven(user_id)
        print(f"🦞 ClawsJoy v{self.VERSION} 启动")
        print(f"👤 用户: {user_id}")
    
    def chat(self, user_input: str) -> str:
        result = self.agent.process(user_input)
        return result['response']
    
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
    
    claws = ClawsJoy(args.user)
    
    if args.message:
        print(f"🤖 {claws.chat(args.message)}")
    else:
        claws.interactive_mode()
