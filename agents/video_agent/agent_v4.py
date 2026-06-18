#!/usr/bin/env python3
"""VideoAgent v4.2 - 精简稳定版（视频助手）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class VideoAgentV4(BusinessAgent):
    """视频 Agent - 精简稳定版"""

    name = "video_agent_v4"
    description = "智慧视频助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.output_dir = Path(f"data/video/{user_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"🎬 VideoAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["分析", "视频分析"]):
            return self._analyze_video(user_input)
        
        if any(kw in t for kw in ["摘要", "总结"]):
            return self._summarize_video(user_input)
        
        if any(kw in t for kw in ["转文字", "字幕", "转录"]):
            return self._transcribe_video(user_input)
        
        if any(kw in t for kw in ["生成脚本", "写脚本", "视频脚本"]):
            return self._generate_script(user_input)
        
        return self._resp("🎬 输入「分析视频」、「视频摘要」、「转文字」或「生成脚本」")

    # ================================================================
    #  分析
    # ================================================================

    def _analyze_video(self, user_input: str) -> Dict:
        content = re.sub(r'分析视频', '', user_input).strip()
        if not content:
            content = "视频内容"
        
        result = self._call_llm(f"分析视频内容：{content}，给出主题、内容、受众、建议")
        return self._resp(f"🎬 视频分析\n\n{result or '分析完成'}")

    # ================================================================
    #  摘要
    # ================================================================

    def _summarize_video(self, user_input: str) -> Dict:
        content = re.sub(r'视频摘要', '', user_input).strip()
        if not content:
            content = "视频内容"
        
        result = self._call_llm(f"生成视频摘要（3-5点）：{content}")
        return self._resp(f"📋 视频摘要\n\n{result or '摘要生成完成'}")

    # ================================================================
    #  转文字
    # ================================================================

    def _transcribe_video(self, user_input: str) -> Dict:
        content = re.sub(r'(转文字|字幕|转录)', '', user_input).strip()
        if not content:
            content = "视频文件"
        
        return self._resp(f"""
📝 视频转文字

视频：{content}

💡 可接入 Whisper API 进行语音识别转录：
```bash
pip install openai-whisper
whisper {content} --model base
"""    )
    def _generate_script(self, user_input: str) -> Dict:
        topic = re.sub(r'(生成脚本|写脚本|视频脚本)', '', user_input).strip()
        if not topic:
            return self._resp("请提供主题。示例：生成脚本 人工智能介绍")

        result = self._call_llm(f"""
为「{topic}」生成视频脚本（3-5分钟）：

格式：【开场】【正文】【总结】
"""    )
        return self._resp(f"🎬 视频脚本\n\n主题：{topic}\n\n{result or self._script_template(topic)}")

    def _script_template(self, topic: str) -> str:
        return f"""
【开场】
大家好，今天我们来聊聊 {topic}。

【正文】

什么是 {topic}

{topic} 的重要性

实际应用案例

【总结】
以上就是关于 {topic} 的介绍，希望对你有帮助！
"""
    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[Video] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = VideoAgentV4("test")
    print(agent.process("生成脚本 人工智能")["response"])     
