"""数字取整"""
class RoundNumberSkill:
    def execute(self, params):
        number = params.get('number', 0)
        decimals = params.get('decimals', 2)
        rounded = round(number, decimals)
        return {"success": True, "original": number, "rounded": rounded}
skill = RoundNumberSkill()
