"""游戏推荐"""
class RecommendGameSkill:
    def execute(self, params):
        platform = params.get('platform', 'mobile')
        genre = params.get('genre', 'rpg')
        games = {"mobile": ["王者荣耀", "原神"], "pc": ["英雄联盟", "绝地求生"]}
        return {"success": True, "games": games.get(platform, []), "message": f"{platform}游戏推荐"}
skill = RecommendGameSkill()
