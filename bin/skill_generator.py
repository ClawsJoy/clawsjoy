#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime

CLAWSJOY_ROOT = Path("/root/clawsjoy")

def generate_skills(tenant_id):
    successes_path = CLAWSJOY_ROOT / f"tenants/tenant_{tenant_id}/agents/main/evolution/SUCCESSES.md"
    if not successes_path.exists():
        print("无成功案例")
        return
    
    content = successes_path.read_text(encoding='utf-8')
    cases = re.split(r'\n##\s+', content)
    
    skills_dir = CLAWSJOY_ROOT / "skills/auto_generated"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    for case in cases:
        if not case.strip():
            continue
        title = case.split('\n')[0].strip()
        skill_name = re.sub(r'[^\w\-]', '', title.replace(' ', '_').lower())[:50]
        skill_path = skills_dir / f"{skill_name}.md"
        
        skill_content = f"""---
name: {skill_name}
type: auto_generated
source: tenant_{tenant_id}
created_at: {datetime.now().isoformat()}
---

# {title}

## 触发条件
当用户需求与以下关键词相关时使用：
- {title.split(':')[0] if ':' in title else title}

## 执行方式
根据成功经验执行对应的脚本。
"""
        skill_path.write_text(skill_content, encoding='utf-8')
        print(f"✅ 生成: {skill_path}")
    
    print(f"共生成 {len(cases)} 个 Skills")

if __name__ == "__main__":
    import sys
    tenant = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_skills(tenant)
