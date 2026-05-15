"""技能加载器 V2 - 支持分类目录"""
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

class SkillLoaderV2:
    """技能加载器 - 支持分类目录"""
    
    def __init__(self, skills_base="skills"):
        self.skills_base = Path(skills_base)
        self.skills = {}
        self.categories = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有分类目录中的技能"""
        categories = ['core', 'math', 'image', 'video', 'text', 'data', 'network']
        
        for cat in categories:
            cat_dir = self.skills_base / cat
            if not cat_dir.exists():
                continue
            
            self.categories[cat] = []
            for py_file in cat_dir.glob("*.py"):
                if py_file.stem == '__init__':
                    continue
                skill_name = py_file.stem
                self.categories[cat].append(skill_name)
                self.skills[skill_name] = {
                    'name': skill_name,
                    'category': cat,
                    'file': str(py_file),
                    'path': f"skills.{cat}.{skill_name}"
                }
                print(f"✅ 加载技能: {cat}/{skill_name}")
    
    def get_skill(self, name: str):
        """获取技能"""
        info = self.skills.get(name)
        if not info:
            return None
        
        try:
            module = importlib.import_module(info['path'])
            if hasattr(module, 'skill'):
                return module.skill
        except Exception as e:
            print(f"加载技能 {name} 失败: {e}")
        return None
    
    def execute(self, name: str, params: Dict) -> Dict:
        """执行技能"""
        skill = self.get_skill(name)
        if skill:
            return skill.execute(params)
        return {"success": False, "error": f"技能不存在: {name}"}
    
    def list_skills(self, category: str = None) -> List[str]:
        """列出技能"""
        if category:
            return self.categories.get(category, [])
        return list(self.skills.keys())
    
    def get_categories(self) -> Dict:
        """获取分类"""
        return self.categories

skill_loader = SkillLoaderV2()
