import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from agents.base_agent import BaseAgent

class YouTubeAgent(BaseAgent):
    def __init__(self):
        super().__init__("youtube_agent", "custom")
    
    def execute(self, params):
        action = params.get("action", "")
        
        if action == "upload":
            from skills.video_uploader import skill
            return skill.execute(params)
        elif action == "analyze":
            from skills.hot_analyzer import skill
            return skill.execute(params)
        else:
            return {"success": False, "error": "未知操作"}

youtube_agent = YouTubeAgent()
