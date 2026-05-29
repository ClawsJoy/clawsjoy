from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""统一技能加载器 - 同时支持 OpenClaw 标准和 ClawsJoy V3"""

from core.lib.skill_loader import SkillLoader as OpenClawLoader
from core.lib.skill_loader_v3 import skill_loader as V3Loader

class UnifiedSkillLoader:
    """统一技能加载器 - 合并两个来源"""
    
    def __init__(self):
        self.openclaw = OpenClawLoader()
        self.v3 = V3Loader
        self._merge()
    
    def _merge(self):
        self._all_skills = {}
        # 添加 V3 技能
        for skill in self.v3.list_all():
            self._all_skills[skill] = {'source': 'v3', 'name': skill}
        # 添加 OpenClaw 技能（不覆盖）
        for skill in self.openclaw.list_all():
            if skill not in self._all_skills:
                self._all_skills[skill] = {'source': 'openclaw', 'name': skill}
    
    def list_skills(self):
        return list(self._all_skills.keys())
    
    def execute(self, skill_name: str, params: dict):
        source = self._all_skills.get(skill_name, {}).get('source')
        if source == 'v3':
            return self.v3.execute(skill_name, params)
        elif source == 'openclaw':
            return self.openclaw.execute_skill(skill_name, params)
        return {"success": False, "error": f"技能不存在: {skill_name}"}
    
    def get_categories(self):
        return self.v3.get_categories()

unified_loader = UnifiedSkillLoader()
