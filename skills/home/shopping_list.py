"""购物清单"""
class ShoppingListSkill:
    def execute(self, params):
        action = params.get('action', 'add')
        item = params.get('item', '')
        return {"success": True, "message": f"已{action} {item} 到购物清单"}
skill = ShoppingListSkill()
