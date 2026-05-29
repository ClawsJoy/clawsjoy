from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""YouTube Agent - YouTube 运营助手"""

from agents.base_agent import BaseAgent
from core.lib.config_manager import config_manager

class YouTubeAgent(SmartAgent):
        import requests
    name = "youtube_agent"
    description = "YouTube运营助手 - 视频上传和频道分析"
    version = "2.0.0"
    type = "custom"
    
    capabilities = [
        {
            "name": "video_upload",
            "description": "上传视频到YouTube",
            "skills": ["video_uploader", "youtube_uploader"],
            "examples": ["上传视频到频道"]
        },
        {
            "name": "channel_analysis",
            "description": "分析频道数据",
            "skills": ["hot_analyzer", "channel_analyst"],
            "examples": ["分析频道表现", "查看播放量"]
        },
        {
            "name": "trend_detection",
            "description": "检测热门趋势",
            "skills": ["hot_collector", "trend_analyzer"],
            "examples": ["当前热门话题", "流行趋势分析"]
        }
    ]
    
    personality = {
        "style": "professional",
        "language": "zh-CN",
        "tone": "formal",
        "greeting": "您好，我是YouTube运营助手，可以帮您管理频道和分析数据。"
    }
    
    def __init__(self):
        super().__init__(
            agent_id="youtube_agent",
            config={
                "name": "YouTube助手",
                "type": "custom",
                "personality": "professional",
                "capabilities": self.capabilities
            }
        )
        self.remember("YouTube Agent 已启动", shared=True)
    
    def execute(self, params):
        action = params.get("action", "")
        
        if action == "upload":
            from skills.video.video_uploader import skill
            return skill.execute(params)
        elif action == "analyze":
            from skills.hot_analyzer import skill
            return skill.execute(params)
        
        return {"success": False, "error": f"未知操作: {action}"}

youtube_agent = YouTubeAgent()
