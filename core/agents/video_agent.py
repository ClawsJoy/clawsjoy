"""Video Agent - 视频制作助手"""

from agents.base_agent import BaseAgent

class VideoAgent(BaseAgent):
    name = "video_agent"
    description = "视频制作助手 - 制作漫剧视频"
    version = "2.0.0"
    type = "custom"
    
    capabilities = [
        {
            "name": "video_creation",
            "description": "从主题生成完整视频",
            "skills": ["manju_maker", "complete_video_maker"],
            "examples": ["制作香港介绍视频", "生成产品宣传片"]
        },
        {
            "name": "subtitle_addition",
            "description": "为视频添加字幕",
            "skills": ["add_subtitles"],
            "examples": ["给视频加字幕"]
        },
        {
            "name": "video_composition",
            "description": "合成多段视频",
            "skills": ["video_composer", "ffmpeg_video"],
            "examples": ["合并多个视频片段"]
        }
    ]
    
    personality = {
        "style": "creative",
        "language": "zh-CN",
        "tone": "casual",
        "greeting": "嗨！我是视频制作助手，可以帮你快速生成漫剧视频。"
    }
    
    def __init__(self):
        super().__init__(
            agent_id="video_agent",
            config={
                "name": "视频制作助手",
                "type": "custom",
                "personality": "creative",
                "capabilities": self.capabilities
            }
        )
        self.remember("Video Agent 已启动", shared=True)
    
    def execute(self, params):
        topic = params.get("topic", "")
        if not topic:
            return {"success": False, "error": "需要提供主题"}
        
        self.remember(f"制作视频: {topic[:50]}", shared=True)
        
        from skills.video.manju_maker import skill
        return skill.execute({"topic": topic})

video_agent = VideoAgent()
