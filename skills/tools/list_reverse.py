"""
列表反转
"""
class List_reverseSkill:
    name = "list_reverse"
    description = "列表反转"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        lst = params.get('list', []); result = list(reversed(lst))
        return {"success": True, "result": result}

skill = List_reverseSkill()
