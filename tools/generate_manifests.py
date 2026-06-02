#!/usr/bin/env python3
"""
为所有技能生成 OpenClaw 兼容的 manifest.json
实现技能生态双向兼容
"""

import json
import yaml
from pathlib import Path
from datetime import datetime

def generate_manifest(skill_path: Path) -> dict:
    """为单个技能生成 manifest"""
    skill_name = skill_path.stem
    category = skill_path.parent.name
    
    # 尝试读取 SKILL.md 获取描述
    skill_md = skill_path.parent / "SKILL.md"
    description = f"{category} 技能"
    use_when = ""
    
    if skill_md.exists():
        content = skill_md.read_text()
        if content.startswith('---'):
            # 解析 YAML frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 2:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    description = frontmatter.get('description', description)
                    use_when = frontmatter.get('use_when', '')
                except:
                    pass
    
    manifest = {
        "name": skill_name,
        "type": "atomic",
        "version": "1.0.0",
        "description": description[:200],
        "category": category,
        "author": "ClawsJoy",
        "compatible_with": ["openclaw", "clawsjoy"],
        "tags": [category],
        "input_schema": {},
        "output_schema": {},
        "examples": []
    }
    
    if use_when:
        manifest["use_when"] = use_when
    
    return manifest

def main():
    """为所有技能生成 manifest.json"""
    skills_dir = Path("skills")
    output_dir = Path("data/skill_manifests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_manifests = {}
    
    for skill_file in skills_dir.rglob("*.py"):
        if skill_file.stem == "__init__":
            continue
        
        manifest = generate_manifest(skill_file)
        all_manifests[skill_file.stem] = manifest
        
        # 同时保存到技能目录
        manifest_file = skill_file.parent / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    # 保存完整索引
    index_file = output_dir / "all_manifests.json"
    with open(index_file, 'w') as f:
        json.dump(all_manifests, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已生成 {len(all_manifests)} 个 manifest.json")
    print(f"   - 技能目录: 各技能目录下 manifest.json")
    print(f"   - 索引文件: {index_file}")

if __name__ == "__main__":
    main()
