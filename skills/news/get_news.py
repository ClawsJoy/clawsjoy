"""获取新闻资讯"""
class GetNewsSkill:
    def execute(self, params):
        category = params.get('category', 'top')
        return {
            "success": True,
            "news": [],
            "message": f"{category} 新闻列表"
        }
skill = GetNewsSkill()
