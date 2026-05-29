"""统一技能管理器 - 融合新旧架构的所有技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from typing import Dict, List, Optional
import importlib

class UnifiedSkillManager:
    """统一管理新旧架构的所有技能"""
    
    def __init__(self):
        self.new_skills = {}   # 新架构原子技能
        self.old_skills = {}   # 旧架构技能
        self.workflows = {}    # 工作流
        self._load_all()
    
    def _load_all(self):
        """加载所有技能"""
        # 1. 加载新架构原子技能
        try:
            import src.api.gateway as gateway
            if hasattr(gateway, '_skills'):
                self.new_skills = gateway._skills.copy()
                print(f"✅ 加载新架构原子技能: {len(self.new_skills)} 个")
        except Exception as e:
            print(f"⚠️ 加载新架构技能失败: {e}")
        
        # 2. 加载旧架构技能
        try:
            from lib.skill_loader_v3 import skill_loader
            old_skills_list = skill_loader.list_all()
            for skill_name in old_skills_list:
                self.old_skills[skill_name] = {
                    'name': skill_name,
                    'source': 'legacy',
                    'loader': skill_loader
                }
            print(f"✅ 加载旧架构技能: {len(self.old_skills)} 个")
        except Exception as e:
            print(f"⚠️ 加载旧架构技能失败: {e}")
        
        # 3. 加载工作流
        try:
            import src.api.gateway as gateway
            if hasattr(gateway, '_workflows'):
                self.workflows = gateway._workflows.copy()
                print(f"✅ 加载工作流: {len(self.workflows)} 个")
        except Exception as e:
            print(f"⚠️ 加载工作流失败: {e}")
    
    def get_all_skills(self) -> Dict:
        """获取所有技能"""
        return {
            "atomic": list(self.new_skills.keys()),
            "legacy": list(self.old_skills.keys()),
            "workflows": list(self.workflows.keys()),
            "total": len(self.new_skills) + len(self.old_skills) + len(self.workflows)
        }
    
    def execute(self, skill_name: str, params: Dict) -> Dict:
        """统一执行入口"""
        # 优先尝试新架构
        if skill_name in self.new_skills:
            try:
                return self.new_skills[skill_name].execute(params)
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 尝试工作流
        if skill_name in self.workflows:
            try:
                return self.workflows[skill_name].execute(params)
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 尝试旧架构
        if skill_name in self.old_skills:
            try:
                skill_info = self.old_skills[skill_name]
                return skill_info['loader'].execute(skill_name, params)
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": f"技能不存在: {skill_name}"}
    
    def search(self, keyword: str) -> List[str]:
        """搜索技能"""
        keyword_lower = keyword.lower()
        results = []
        
        for name in self.new_skills.keys():
            if keyword_lower in name.lower():
                results.append(f"[新] {name}")
        
        for name in self.old_skills.keys():
            if keyword_lower in name.lower():
                results.append(f"[旧] {name}")
        
        for name in self.workflows.keys():
            if keyword_lower in name.lower():
                results.append(f"[流] {name}")
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "new_architecture": len(self.new_skills),
            "legacy": len(self.old_skills),
            "workflows": len(self.workflows),
            "total": len(self.new_skills) + len(self.old_skills) + len(self.workflows)
        }

unified_manager = UnifiedSkillManager()
