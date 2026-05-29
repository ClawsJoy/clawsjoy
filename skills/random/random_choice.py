"""随机选择"""
import random
class RandomChoiceSkill:
    def execute(self, params):
        items = params.get('items', [])
        count = params.get('count', 1)
        if not items:
            return {"success": False, "error": "列表为空"}
        selected = random.sample(items, min(count, len(items)))
        return {"success": True, "selected": selected if count > 1 else selected[0]}
skill = RandomChoiceSkill()
