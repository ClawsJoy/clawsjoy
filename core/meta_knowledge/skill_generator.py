"""技能自生成器 - 从成功组合中学习并生成新技能"""

import json
import re
from pathlib import Path
from datetime import datetime


class SkillGenerator:
    """自动技能生成器"""
    
    def __init__(self):
        self.combos_file = Path("data/skill_stats/successful_combos.json")
        self.generated_dir = Path("skills/auto_generated")
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self._load_combos()
    
    def _load_combos(self):
        if self.combos_file.exists():
            with open(self.combos_file, 'r') as f:
                self.combos = json.load(f)
        else:
            self.combos = {"combos": [], "stats": {}}
    
    def analyze_and_generate(self):
        """分析成功组合，生成新技能"""
        generated = []
        
        # 按技能组合频率分组
        combo_frequency = {}
        for combo in self.combos.get("combos", []):
            skills = combo.get("skills", [])
            if len(skills) >= 2:
                key = "|".join(skills)
                if key not in combo_frequency:
                    combo_frequency[key] = {
                        "skills": skills,
                        "count": 0,
                        "intents": []
                    }
                combo_frequency[key]["count"] += 1
                combo_frequency[key]["intents"].append(combo.get("intent", ""))
        
        # 高频组合自动生成新技能
        for key, data in combo_frequency.items():
            if data["count"] >= 3:
                skill_name = self._generate_skill_name(data["skills"])
                skill_code = self._generate_skill_code(skill_name, data["skills"])
                
                skill_file = self.generated_dir / f"{skill_name}.py"
                if not skill_file.exists():
                    with open(skill_file, 'w') as f:
                        f.write(skill_code)
                    generated.append(skill_name)
                    print(f"✨ 自动生成新技能: {skill_name}")
        
        return generated
    
    def _generate_skill_name(self, skills: list) -> str:
        """生成技能名称"""
        base = skills[0] if skills else "auto"
        return f"auto_{base}_combo"
    
    def _generate_skill_code(self, skill_name: str, skills: list) -> str:
        """生成技能代码"""
        return f'''"""
自动生成技能: {' → '.join(skills)}
生成时间: {datetime.now().isoformat()}
"""

from core.lib.skill_loader_v3 import skill_loader


class {skill_name.replace('_', ' ').title().replace(' ', '')}Skill:
    """自动生成的组合技能"""
    
    name = "{skill_name}"
    description = "自动生成的组合技能"
    version = "1.0.0"
    category = "auto_generated"
    
    def __init__(self):
        self.composed_skills = {skills}
    
    def execute(self, params: dict) -> dict:
        results = {{}}
        for skill_name in self.composed_skills:
            result = skill_loader.execute(skill_name, params)
            results[skill_name] = result
            if not result.get("success"):
                return {{
                    "success": False,
                    "failed_at": skill_name,
                    "error": result.get("error")
                }}
        
        final = results.get(skills[-1], {{}})
        return {{
            "success": True,
            "result": final.get("result"),
            "steps": results
        }}


skill = {skill_name.replace('_', ' ').title().replace(' ', '')}Skill()
'''
