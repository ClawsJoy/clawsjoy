"""技能加载器 - 基于声明式配置加载技能"""
import yaml
import importlib
from pathlib import Path
from typing import Dict, List, Optional

class SkillLoader:
    """技能加载器，支持声明式注册"""
    
    def __init__(self, skills_config_dir="config/skills"):
        self.skills_config_dir = Path(skills_config_dir)
        self.skills = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有技能声明"""
        if not self.skills_config_dir.exists():
            print(f"⚠️ 技能配置目录不存在: {self.skills_config_dir}")
            return
        
        for yaml_file in self.skills_config_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                skill_name = config.get('name')
                if skill_name:
                    self.skills[skill_name] = config
                    print(f"✅ 加载技能声明: {skill_name}")
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """获取技能信息"""
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """列出所有已声明的技能"""
        return list(self.skills.keys())
    
    def get_skill_by_tag(self, tag: str) -> List[Dict]:
        """根据标签查找技能"""
        result = []
        for name, info in self.skills.items():
            if tag in info.get('tags', []):
                result.append(info)
        return result
    
    def execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """执行技能"""
        try:
            module = importlib.import_module(f"skills.{skill_name}")
            if hasattr(module, 'skill'):
                return module.skill.execute(params)
            else:
                return {"success": False, "error": f"技能 {skill_name} 无实例"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# 全局实例
skill_loader = SkillLoader()
