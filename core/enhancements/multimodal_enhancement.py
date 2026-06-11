"""多模态统一调用 - 可选插件"""

class MultimodalEnhancement:
    """多模态统一调用"""
    
    def __init__(self):
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        try:
            from agents.vision_agent.agent import VisionAgent
            self.agents['vision'] = VisionAgent()
        except: pass
        
        try:
            from agents.audio_agent.agent import AudioAgent
            self.agents['audio'] = AudioAgent()
        except: pass
        
        try:
            from agents.video_agent.agent import VideoAgent
            self.agents['video'] = VideoAgent()
        except: pass
    
    def process(self, modality: str, input_data: str):
        if modality in self.agents:
            return self.agents[modality]._execute_business(input_data, {})
        return {"error": f"不支持的模态: {modality}"}

multimodal_enhancement = MultimodalEnhancement()
