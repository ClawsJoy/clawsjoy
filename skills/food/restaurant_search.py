"""餐厅搜索"""
class RestaurantSearchSkill:
    def execute(self, params):
        cuisine = params.get('cuisine', '')
        location = params.get('location', '')
        return {"success": True, "restaurants": [], "message": f"搜索{cuisine}餐厅"}
skill = RestaurantSearchSkill()
