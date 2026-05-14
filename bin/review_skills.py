#!/usr/bin/env python3
"""人工复检工具"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from lib.skill_registry import skill_registry

def main():
    pending = skill_registry.get_pending()
    
    if not pending:
        print("✅ 没有待复检的技能")
        return
    
    print(f"📋 待复检技能 ({len(pending)}个):\n")
    
    for p in pending:
        print(f"ID: {p['id']}")
        print(f"需求: {p['requirement']}")
        print(f"技能名: {p['skill_name']}")
        print(f"代码预览:\n{p['code_preview']}...")
        print("-" * 40)
        
        action = input("批准? (y/n/skip): ").strip().lower()
        
        if action == 'y':
            # 批准：移动到 skills 目录
            import shutil
            from pathlib import Path
            src = Path(f"skills/pending/{p['skill_name']}.py")
            dst = Path(f"skills/{p['skill_name']}.py")
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"✅ 已批准，移动到 {dst}")
            skill_registry.review(p['id'], True, "人工审核通过")
        elif action == 'n':
            comment = input("拒绝原因: ")
            skill_registry.review(p['id'], False, comment)
            print(f"❌ 已拒绝")
        else:
            print("⏭️ 跳过")

if __name__ == "__main__":
    main()
