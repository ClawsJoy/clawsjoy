#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/d/clawsjoy/skills')
from ops_skills import OpsSkills

ops = OpsSkills()
print("开始运维...")

for skill in ["fix_agent_api", "fix_chat_api", "fix_promo_api", "fix_web"]:
    result = ops.execute(skill)
    print(f"{skill}: {result['message']}")
