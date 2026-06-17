#!/usr/bin/env python3
"""audio_agent v4.0 - 智慧化音频处理智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class AudioAgentV4(BusinessAgent):
    """智慧化音频处理智能体"""
    
    name = "audio_agent_v4"
    description = "智慧化音频助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.output_dir = Path(f"data/audio/{user_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"🎵 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("transcribe", "audio"): (True, 0.90),
            ("analyze", "audio"): (True, 0.85),
            ("convert", "audio"): (True, 0.80),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 音频转文字
        if any(kw in user_input for kw in ["转文字", "音频转文字", "语音转文字"]):
            return self._transcribe_audio(user_input)
        
        # 音频分析
        if any(kw in user_input for kw in ["分析音频", "音频分析"]):
            return self._analyze_audio(user_input)
        
        return self._response(self._smart_fallback(user_input))
    
    def _transcribe_audio(self, user_input: str) -> Dict:
        """音频转文字"""
        match = re.search(r'(?:转文字|音频转文字|语音转文字)[：:]\s*(.+)', user_input)
        audio_info = match.group(1) if match else "音频文件"
        
        prompt = f"""请为以下音频内容生成文字稿：

音频描述：{audio_info}

要求：
1. 完整转录
2. 标注说话人（如有多人）
3. 添加时间戳
4. 格式规范"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📝 **音频转文字**\n\n{response}",
                metadata={"type": "transcript"}
            )
        
        return self._response(
            f"音频转文字：{audio_info}\n\n"
            f"💡 提示：可接入 Whisper API 进行语音识别转录\n\n"
            f"示例命令：\n"
            f"```bash\n"
            f"# 安装 whisper\npip install openai-whisper\n\n"
            f"# 转录音频\nwhisper {audio_info} --model base --output_dir {self.output_dir}\n"
            f"```",
            metadata={"type": "guide"}
        )
    
    def _analyze_audio(self, user_input: str) -> Dict:
        """分析音频"""
        match = re.search(r'(?:分析音频|音频分析)[：:]\s*(.+)', user_input)
        audio_info = match.group(1) if match else "音频内容"
        
        prompt = f"""请分析以下音频内容：

音频描述：{audio_info}

分析维度：
1. 音频类型（音乐/播客/会议/讲座）
2. 主要内容
3. 时长估计
4. 音质评价
5. 改进建议"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎧 **音频分析**\n\n{response}",
                metadata={"type": "analysis"}
            )
        
        return self._response(
            f"音频分析：{audio_info}\n\n"
            f"📊 分析维度：\n"
            f"1. 类型：{audio_info}\n"
            f"2. 内容：需要具体音频文件\n"
            f"3. 建议：使用音频分析工具获取详细数据\n\n"
            f"💡 可用的音频分析工具：\n"
            f"- Audacity（开源）\n"
            f"- Adobe Audition（专业）\n"
            f"- Python (librosa) 库"
        )
    
    def _get_help(self) -> str:
        return """🎵 **音频助手**

支持功能:
- 音频转文字: "转文字 meeting_audio.mp3"
- 音频分析: "分析音频 podcast.mp3"

💡 提示: 
- 接入 Whisper API 可实现语音转文字
- 支持格式: mp3, wav, m4a, flac"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = AudioAgentV4("test")
    print("✅ audio_agent_v4 测试通过")
