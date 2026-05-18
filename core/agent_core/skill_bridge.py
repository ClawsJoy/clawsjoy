from lib.smart_config import smart_config

# 自愈技能
if "self_heal" not in skill_bridge.verified_skills:
    skill_bridge.verified_skills.append("self_heal")
