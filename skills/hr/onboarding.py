"""新员工入职流程"""
class OnboardingSkill:
    def execute(self, params):
        name = params.get('name', '')
        department = params.get('department', '')
        return {"success": True, "tasks": ["账号创建", "工位分配", "培训安排"], "message": f"{name} 入职流程已启动"}
skill = OnboardingSkill()
