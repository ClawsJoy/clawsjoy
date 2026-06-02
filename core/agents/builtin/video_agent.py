#!/usr/bin/env python3
"""Video Agent - 视频处理助手

@version: 2.0.0
@author: ClawsJoy
@date: 2026-06-02
"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from skills.video.skill import skill as video_skill


class VideoAgent(SmartAgent):
    name = "video_agent"
    description = "视频处理助手，支持裁剪、转码、合成、字幕、制作"
    type = "core"

    def __init__(self, user_id: str = "default"):
        self._load_agent_config()
        super().__init__(user_id=user_id)
        print(f"🎬 视频Agent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理视频相关请求"""
        msg = user_input.lower()
        
        # 解析意图
        if any(kw in msg for kw in ["裁剪", "截取", "trim"]):
            return self._trim(user_input)
        elif any(kw in msg for kw in ["转码", "转换", "transcode"]):
            return self._transcode(user_input)
        elif any(kw in msg for kw in ["截图", "帧", "screenshot"]):
            return self._screenshot(user_input)
        elif any(kw in msg for kw in ["合成", "合并", "compose"]):
            return self._compose(user_input)
        elif any(kw in msg for kw in ["字幕", "subtitle"]):
            return self._subtitle(user_input)
        elif any(kw in msg for kw in ["制作", "生成视频", "make"]):
            return self._make(user_input)
        else:
            return self._info()
    
    def _trim(self, user_input: str) -> Dict:
        """裁剪视频"""
        result = video_skill.execute({
            "action": "ffmpeg",
            "action_type": "trim",
            "video_path": "input.mp4",
            "start": "00:00:00",
            "duration": 10
        })
        return {"success": True, "response": "视频裁剪完成", "agent": self.name, "data": result}
    
    def _transcode(self, user_input: str) -> Dict:
        """转码视频"""
        result = video_skill.execute({
            "action": "ffmpeg",
            "action_type": "transcode",
            "video_path": "input.mp4",
            "format": "mp4"
        })
        return {"success": True, "response": "视频转码完成", "agent": self.name, "data": result}
    
    def _screenshot(self, user_input: str) -> Dict:
        """截图"""
        result = video_skill.execute({
            "action": "ffmpeg",
            "action_type": "screenshot",
            "video_path": "input.mp4",
            "timestamp": "00:00:01"
        })
        return {"success": True, "response": "截图已保存", "agent": self.name, "data": result}
    
    def _compose(self, user_input: str) -> Dict:
        """合成视频"""
        result = video_skill.execute({
            "action": "compose",
            "video_paths": ["video1.mp4", "video2.mp4"]
        })
        return {"success": True, "response": "视频合成完成", "agent": self.name, "data": result}
    
    def _subtitle(self, user_input: str) -> Dict:
        """添加字幕"""
        import re
        text_match = re.search(r'["\']([^"\']+)["\']', user_input)
        text = text_match.group(1) if text_match else "测试字幕"
        result = video_skill.execute({
            "action": "subtitle",
            "video_path": "input.mp4",
            "text": text
        })
        return {"success": True, "response": f"已添加字幕: {text}", "agent": self.name, "data": result}
    
    def _make(self, user_input: str) -> Dict:
        """制作视频"""
        import re
        duration_match = re.search(r'(\d+)\s*秒', user_input)
        duration = int(duration_match.group(1)) if duration_match else 5
        result = video_skill.execute({
            "action": "make",
            "title": user_input[:20],
            "duration": duration,
            "color": "blue"
        })
        return {"success": True, "response": f"视频制作完成，时长{duration}秒", "agent": self.name, "data": result}
    
    def _info(self) -> Dict:
        """返回帮助信息"""
        return {
            "success": True,
            "response": "我可以帮你处理视频：裁剪、转码、截图、合成、添加字幕、制作视频",
            "agent": self.name,
            "actions": ["trim", "transcode", "screenshot", "compose", "subtitle", "make"]
        }


# 按需创建实例（不使用全局实例）
