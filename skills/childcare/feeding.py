"""喂养记录"""
class FeedingSkill:
    def execute(self, params):
        time = params.get('time', '')
        amount = params.get('amount', '')
        food = params.get('food', '')
        return {"success": True, "message": f"{time} 喂养 {food} {amount}"}
skill = FeedingSkill()
