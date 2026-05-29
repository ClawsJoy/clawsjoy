"""列表过滤"""
class FilterListSkill:
    def execute(self, params):
        items = params.get('items', [])
        keyword = params.get('keyword', '')
        filtered = [i for i in items if keyword.lower() in str(i).lower()]
        return {"success": True, "filtered": filtered, "count": len(filtered)}
skill = FilterListSkill()
