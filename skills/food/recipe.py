"""菜谱推荐"""
class RecipeSkill:
    def execute(self, params):
        dish = params.get('dish', '')
        ingredient = params.get('ingredient', '')
        recipes = {
            "番茄炒蛋": ["番茄2个", "鸡蛋3个", "盐", "糖"],
            "红烧肉": ["五花肉500g", "酱油", "冰糖", "姜"]
        }
        result = recipes.get(dish, ["食材准备", "烹饪步骤1", "烹饪步骤2"])
        return {"success": True, "ingredients": result, "message": f"{dish}菜谱"}
skill = RecipeSkill()
