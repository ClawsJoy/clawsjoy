"""讲故事"""
class StorySkill:
    def execute(self, params):
        age = params.get('age', 5)
        theme = params.get('theme', 'friendship')
        stories = {
            "friendship": "从前有两只小兔子，他们是好朋友...",
            "bravery": "勇敢的小狮子面对困难从不退缩...",
            "kindness": "善良的小女孩帮助了受伤的小鸟..."
        }
        story = stories.get(theme, stories["friendship"])
        return {"success": True, "story": story, "duration": 3, "message": f"适合{age}岁的故事"}
skill = StorySkill()
