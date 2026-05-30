#!/usr/bin/env python3
"""Skill Loader V3 - Skill Loader V3 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from pathlib import Path
from typing import Dict, List, Optional


class SkillLoaderV3:
    """统一技能加载器 - 支持分类目录"""

    def __init__(self):
        self.skills = {}
        self.categories = {}
        self._load_all()

    def _load_all(self):
        """加载所有分类目录中的技能 - 直接扫描 skills 目录"""
        skills_root = Path("skills")
        if not skills_root.exists():
            print(f"⚠️ skills 目录不存在: {skills_root}")
            return

        for cat_dir in skills_root.iterdir():
            if not cat_dir.is_dir():
                continue
            if cat_dir.name.startswith('.'):
                continue

            cat_name = cat_dir.name
            self.categories[cat_name] = []

            for py_file in cat_dir.glob("*.py"):
                if py_file.stem == '__init__':
                    continue
                skill_name = py_file.stem
                self.categories[cat_name].append(skill_name)
                self.skills[skill_name] = {
                    'name': skill_name,
                    'category': cat_name,
                    'category_name': cat_name,
                    'file': str(py_file),
                    'path': f"skills.{cat_name}.{skill_name}"
                }

        print(f"✅ 技能加载器 V3 已初始化")
        print(f"   总技能: {len(self.skills)} 个")
        for cat, skills in self.categories.items():
            if skills:
                print(f"   {cat}: {len(skills)} 个")

    def list_skills(self, category: str = None) -> Dict:
        """列出所有技能"""
        if category and category in self.categories:
            return {s: self.skills[s] for s in self.categories[category]}
        return self.skills

    def get_skill(self, name: str):
        """获取技能信息"""
        return self.skills.get(name)

    def execute(self, skill_name: str, params: dict) -> dict:
        """执行技能"""
        skill_info = self.skills.get(skill_name)
        if not skill_info:
            return {"success": False, "error": f"技能 {skill_name} 不存在"}

        try:
            # 动态导入技能模块
            module_path = skill_info['path']
            module = __import__(module_path, fromlist=['skill'])
            if hasattr(module, 'skill') and hasattr(module.skill, 'execute'):
                result = module.skill.execute(params)
                return {"success": True, "result": result, "skill": skill_name}
            else:
                return {"success": False, "error": f"技能 {skill_name} 格式不正确"}
        except Exception as e:
            return {"success": False, "error": str(e)}



    def search_skills(self, keyword: str) -> list:
        """搜索技能（基于关键词）"""
        keyword_lower = keyword.lower()
        results = []
        for skill_name, info in self.skills.items():
            if keyword_lower in skill_name.lower():
                results.append(skill_name)
            elif 'category' in info and keyword_lower in info.get('category_name', '').lower():
                results.append(skill_name)
        return results[:20]

    def get_categories(self) -> Dict:
        """获取分类"""
        return self.categories


# 全局实例
skill_loader = SkillLoaderV3()
