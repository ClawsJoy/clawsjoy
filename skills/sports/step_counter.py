"""计步器"""
class StepCounterSkill:
    def execute(self, params):
        today_steps = params.get('steps', 0)
        target = params.get('target', 10000)
        return {"success": True, "steps": today_steps, "target": target, "progress": f"{today_steps/target*100:.0f}%"}
skill = StepCounterSkill()
