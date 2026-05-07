#!/usr/bin/env python3
"""运维 Agent"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy/skills')
from ops_skills import OpsSkills

class OpsAgent:
    def __init__(self):
        self.ops = OpsSkills()
    
    def auto_heal(self):
        print("开始自动运维...")
        skills = ["fix_agent_api", "fix_chat_api", "fix_promo_api"]
        for skill in skills:
            result = self.ops.execute(skill)
            print(f"{skill}: {result.get('message')}")

if __name__ == "__main__":
    agent = OpsAgent()
    agent.auto_heal()
