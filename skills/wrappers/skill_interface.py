"""技能接口 - 包装器基类"""
class SkillInterface:
    """技能接口定义"""
    @staticmethod
    def get_skill(name):
        """获取技能"""
        try:
            from lib.skill_loader_v3 import skill_loader
            return skill_loader.get_skill(name)
        except:
            return None
    
    @staticmethod
    def list_skills():
        """列出所有技能"""
        try:
            from lib.skill_loader_v3 import skill_loader
            return skill_loader.list_skills()
        except:
            return []

skill_interface = SkillInterface()
