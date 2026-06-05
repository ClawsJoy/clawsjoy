#!/usr/bin/env python3
#!/usr/bin/env python3
"""Index Vector Knowledge - Index Vector Knowledge 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys

sys.path.insert(0, ".")


def main():
    from pathlib import Path

    from core.lib.skill_loader_v3 import skill_loader
    from core.lib.vector_knowledge_center import vector_knowledge_center

    print("📚 索引技能...")
    for category, skills in skill_loader.categories.items():
        for skill in skills:
            skill_name = skill.get("name") if isinstance(skill, dict) else str(skill)
            vector_knowledge_center.add_skill(
                skill_name,
                {"category": category, "description": f"技能分类: {category}"},
            )

    print("🤖 索引 Agent...")
    agent_dir = Path("core/agents/builtin")
    for agent_file in agent_dir.glob("*.py"):
        agent_name = agent_file.stem
        if agent_name.startswith("__"):
            continue
        vector_knowledge_center.add_agent(
            agent_name, {"type": "core", "description": f"Agent: {agent_name}"}
        )

    print("✅ 索引完成")
    for name, col in vector_knowledge_center.collections.items():
        print(f"   {name}: {col.count()} 条")


if __name__ == "__main__":
    main()
