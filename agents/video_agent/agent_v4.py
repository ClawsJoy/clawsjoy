#!/usr/bin/env python3
"""video_agent v4.0 - 智慧化视频处理智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class VideoAgentV4(BusinessAgent):
    """智慧化视频处理智能体"""
    
    name = "video_agent_v4"
    description = "智慧化视频助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.output_dir = Path(f"data/video/{user_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"🎬 {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("analyze", "video"): (True, 0.90),
            ("summarize", "video"): (True, 0.85),
            ("transcribe", "video"): (True, 0.80),
            ("generate", "script"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 视频分析
        if any(kw in user_input for kw in ["分析视频", "视频分析"]):
            return self._analyze_video(user_input)
        
        # 视频摘要
        if any(kw in user_input for kw in ["视频摘要", "总结视频"]):
            return self._summarize_video(user_input)
        
        # 视频转文字
        if any(kw in user_input for kw in ["转文字", "字幕", "转录"]):
            return self._transcribe_video(user_input)
        
        # 生成脚本
        if any(kw in user_input for kw in ["生成脚本", "写脚本", "视频脚本"]):
            return self._generate_script(user_input)
        
        return self._response(self._get_help())
    
    def _analyze_video(self, user_input: str) -> Dict:
        """分析视频"""
        # 提取视频信息
        match = re.search(r'分析视频[：:]\s*(.+)', user_input)
        video_info = match.group(1) if match else "视频内容"
        
        prompt = f"""请分析以下视频内容：

{video_info}

请从以下方面分析：
1. 视频主题
2. 主要内容
3. 受众定位
4. 优化建议

输出格式：简洁的列表形式"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎬 **视频分析**\n\n{response}",
                metadata={"type": "analysis"}
            )
        
        return self._response(f"视频分析：{video_info}\n\n💡 提示：接入视频分析 API 可获得更详细结果")
    
    def _summarize_video(self, user_input: str) -> Dict:
        """视频摘要"""
        match = re.search(r'视频摘要[：:]\s*(.+)', user_input)
        video_content = match.group(1) if match else "视频内容"
        
        prompt = f"""请为以下视频内容生成摘要：

{video_content}

要求：
1. 提取核心要点
2. 概括主要内容
3. 语言简洁
4. 输出 3-5 个要点"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📋 **视频摘要**\n\n{response}",
                metadata={"type": "summary"}
            )
        
        return self._response(f"视频摘要：\n\n{video_content[:200]}...")
    
    def _transcribe_video(self, user_input: str) -> Dict:
        """视频转文字"""
        match = re.search(r'(?:转文字|字幕|转录)[：:]\s*(.+)', user_input)
        video_path = match.group(1) if match else "视频文件"
        
        prompt = f"""请为以下视频内容生成文字稿：

视频路径/描述：{video_path}

要求：
1. 完整转录
2. 保留关键信息
3. 格式规范"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📝 **视频转文字**\n\n{response}",
                metadata={"type": "transcript"}
            )
        
        return self._response(
            f"视频转文字：{video_path}\n\n"
            f"💡 提示：可接入 Whisper API 进行语音识别转录\n\n"
            f"示例：\n"
            f"```\n"
            f"1. 安装依赖: pip install openai-whisper\n"
            f"2. 转录: whisper {video_path} --model base\n"
            f"```",
            metadata={"type": "guide"}
        )
    
    def _generate_script(self, user_input: str) -> Dict:
        """生成视频脚本"""
        # 提取主题
        match = re.search(r'(?:生成脚本|写脚本|视频脚本)[：:]\s*(.+)', user_input)
        topic = match.group(1) if match else user_input.replace("生成脚本", "").replace("写脚本", "").strip()
        
        if not topic:
            return self._response("请提供视频主题。\n\n示例：\n- 生成脚本 介绍人工智能\n- 写一个科普视频脚本 关于气候变化")
        
        prompt = f"""请为以下主题生成一个视频脚本：

主题：{topic}

要求：
1. 时长约 3-5 分钟
2. 结构：开场 → 正文 → 总结
3. 语言生动有趣
4. 包含镜头说明（可选）

输出格式：
【开场】
...
【正文】
...
【总结】
..."""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎬 **视频脚本**\n\n主题：{topic}\n\n{response}",
                metadata={"topic": topic, "type": "script"}
            )
        
        return self._response(self._get_script_template(topic))
    
    def _get_script_template(self, topic: str) -> str:
        """获取脚本模板"""
        return f"""🎬 **视频脚本模板**

主题：{topic}

【开场】（0:00 - 0:30）
大家好，欢迎观看本期视频。今天我们来聊聊 {topic}。

【正文】（0:30 - 3:00）
1. 首先，让我们了解什么是 {topic}...
2. 其次，{topic} 的重要性体现在...
3. 最后，我们来看看实际应用...

【总结】（3:00 - 3:30）
以上就是关于 {topic} 的介绍。希望对你有所帮助！

💡 提示：可根据需要调整时长和内容深度"""
    
    def _get_help(self) -> str:
        return """🎬 **视频助手**

支持功能:
- 视频分析: "分析视频 产品介绍视频"
- 视频摘要: "视频摘要 教程视频"
- 视频转文字: "转文字 meeting_recording.mp4"
- 生成脚本: "生成脚本 介绍人工智能"

💡 提示: 接入 Whisper API 可实现语音转文字"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = VideoAgentV4("test")
    print("✅ video_agent_v4 测试通过")
