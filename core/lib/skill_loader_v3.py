#!/usr/bin/env python3
"""技能加载器 V3"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from core.lib.unified_config import unified_config


class SkillLoaderV3:
    """技能加载器 V3"""

    def __init__(self):
        self.skills = {}
        self.categories = {}
        self._load_all()

    def _load_all(self):
        """加载所有技能"""
        skills_dir = Path("skills")
        if not skills_dir.exists():
            return
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            # 查找 SKILL.md 或 manifest.json
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            
            # 解析技能信息
            name = skill_dir.name
            with open(skill_file, 'r') as f:
                content = f.read()
            
            # 提取类别
            category = "general"
            if "category:" in content:
                for line in content.split('\n'):
                    if line.startswith("category:"):
                        category = line.split(":", 1)[1].strip()
                        break
            
            self.skills[name] = {
                "name": name,
                "category": category,
                "file": str(skill_file),
                "path": f"skills.{name}",
                "category_name": category
            }
            
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)

    def list_skills(self, category: str = None) -> Dict:
        """列出所有技能"""
        if category and category in self.categories:
            return {s: self.skills[s] for s in self.categories[category]}
        return self.skills

    def get_skill(self, name: str) -> Optional[Dict]:
        """获取技能信息"""
        return self.skills.get(name)

    def execute(self, skill_name: str, params: dict) -> dict:
        """执行技能"""
        try:
            import importlib
            skill_info = self.get_skill(skill_name)
            if not skill_info:
                return {"error": f"技能 {skill_name} 不存在"}
            
            module_path = skill_info["path"]
            module = importlib.import_module(module_path)
            
            if hasattr(module, 'execute'):
                result = module.execute(params)
            elif hasattr(module, 'run'):
                result = module.run(params)
            else:
                result = {"error": f"技能 {skill_name} 没有 execute 或 run 方法"}
            
            return result
        except Exception as e:
            return {"error": str(e)}

    def search_skills(self, keyword: str) -> list:
        """搜索技能"""
        results = []
        keyword_lower = keyword.lower()
        for name, info in self.skills.items():
            if keyword_lower in name.lower() or keyword_lower in info.get("category", "").lower():
                results.append(info)
        return results

    def get_categories(self) -> Dict:
        """获取分类"""
        return self.categories

    def reload(self):
        """重新加载所有技能"""
        self.skills = {}
        self.categories = {}
        self._load_all()
        print(f"✅ 技能已重载，共 {len(self.skills)} 个技能")


skill_loader = SkillLoaderV3()
