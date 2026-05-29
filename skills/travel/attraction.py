"""景点推荐"""
class AttractionSkill:
    def execute(self, params):
        city = params.get('city', '')
        return {"success": True, "attractions": [], "message": f"{city}景点推荐"}
skill = AttractionSkill()
