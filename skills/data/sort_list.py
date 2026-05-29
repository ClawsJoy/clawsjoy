"""列表排序"""
class SortListSkill:
    def execute(self, params):
        items = params.get('items', [])
        reverse = params.get('reverse', False)
        sorted_items = sorted(items, reverse=reverse)
        return {"success": True, "sorted": sorted_items}
skill = SortListSkill()
