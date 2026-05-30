#!/usr/bin/env python3
#!/usr/bin/env python3
"""Reindex Vector Knowledge - Reindex Vector Knowledge 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
sys.path.insert(0, '.')

def main():
    print("="*60)
    print("重新索引向量知识中心")
    print("="*60)
    
    from core.lib.vector_knowledge_center import vector_knowledge_center
    from pathlib import Path
    
    # 1. 索引技能 - 扫描 skills 目录
    print("\n📚 1. 索引技能...")
    skills_root = Path("skills")
    skill_count = 0
    
    if skills_root.exists():
        for category_dir in skills_root.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue
            
            category = category_dir.name
            # 检查是否有 SKILL.md 或 __init__.py 作为技能标志
            if (category_dir / "SKILL.md").exists() or (category_dir / "__init__.py").exists():
                skill_name = category
                vector_knowledge_center.add_skill(skill_name, {
                    "category": category,
                    "description": f"技能: {skill_name}",
                    "keywords": skill_name
                })
                skill_count += 1
                if skill_count % 20 == 0:
                    print(f"   已索引 {skill_count} 个技能")
        
        print(f"   ✅ 索引完成: {skill_count} 个技能")
    else:
        print(f"   ⚠️ skills 目录不存在: {skills_root}")
    
    # 2. 索引 Agent
    print("\n🤖 2. 索引 Agent...")
    agent_dir = Path("core/agents/builtin")
    agent_count = 0
    
    if agent_dir.exists():
        for agent_file in agent_dir.glob("*.py"):
            agent_name = agent_file.stem
            if agent_name.startswith('__') or agent_name.startswith('test'):
                continue
            
            vector_knowledge_center.add_agent(agent_name, {
                "type": "core",
                "description": f"Agent: {agent_name}",
                "capabilities": f"{agent_name} 的功能"
            })
            agent_count += 1
        
        print(f"   ✅ 索引完成: {agent_count} 个 Agent")
    else:
        print(f"   ⚠️ agent 目录不存在: {agent_dir}")
    
    # 3. 显示最终统计
    print("\n📊 最终统计:")
    for name, col in vector_knowledge_center.collections.items():
        print(f"   {name}: {col.count()} 条")
    
    print("\n✅ 索引完成")

if __name__ == "__main__":
    main()
