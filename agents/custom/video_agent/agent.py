import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
from agents.base_agent import BaseAgent

class VideoAgent(BaseAgent):
    def __init__(self):
        super().__init__("video_agent", "custom")
    
    def execute(self, params):
        topic = params.get("topic", "")
        
        # 从记忆恢复偏好
        default_duration = self.recall("default_duration") or 60
        
        from skills.manju_maker import skill
        result = skill.execute({"topic": topic, "target_duration": default_duration})
        
        # 记录
        self.log_conversation(topic, result.get("video", ""))
        
        return result

video_agent = VideoAgent()
