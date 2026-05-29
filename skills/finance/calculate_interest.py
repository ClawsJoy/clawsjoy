"""利息计算"""
class CalculateInterestSkill:
    def execute(self, params):
        principal = params.get('principal', 10000)
        rate = params.get('rate', 3.5)
        years = params.get('years', 1)
        interest = principal * rate / 100 * years
        return {"success": True, "interest": interest, "total": principal + interest}
skill = CalculateInterestSkill()
