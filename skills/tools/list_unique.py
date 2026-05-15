"""
列表去重
"""
class List_uniqueSkill:
    name = "list_unique"
    description = "列表去重"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        lst = params.get('list', []); result = list(set(lst))
        return {"success": True, "result": result}

skill = List_uniqueSkill()
