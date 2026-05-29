from lib.smart_config import smart_config
"""视频制作工作流 - 组合原子技能"""
from src.lib.base_skill import BaseWorkflowSkill

class VideoCreationWorkflow(BaseWorkflowSkill):
    name = "video_creation"
    description = "完整的视频制作工作流"
    version = "1.0.0"
    category = "workflow"
    
    steps = [
        {"skill": "script_generator", "params": {"topic": "{topic}"}, "output": "script"},
        {"skill": "audio_generator", "params": {"text": "{script}"}, "output": "audio"},
        {"skill": "video_composer", "params": {"audio_path": "{audio}"}, "output": "video"}
    ]
    dependencies = ["script_generator", "audio_generator", "video_composer"]

skill = VideoCreationWorkflow()
