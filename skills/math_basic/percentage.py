"""百分比计算"""
class PercentageSkill:
    def execute(self, params):
        part = params.get('part', 0)
        whole = params.get('whole', 1)
        percentage = (part / whole) * 100 if whole != 0 else 0
        return {"success": True, "percentage": round(percentage, 2), "formatted": f"{percentage:.1f}%"}
skill = PercentageSkill()
