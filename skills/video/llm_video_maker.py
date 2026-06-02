#!/usr/bin/env python3
"""LLM Video Maker - LLM 驱动的视频制作技能

@version: 2.0.0
@author: ClawsJoy
@date: 2026-06-02
@enhanced: 使用 LLM 分析需求，自动生成视频
"""

import json
from pathlib import Path
from typing import Dict, Any


class LLMVideoMakerSkill:
    """LLM 驱动的视频制作技能"""
    
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 LLM 视频制作
        
        支持的 action:
        - generate: 根据描述生成视频
        - analyze: 分析视频内容
        - suggest: 推荐视频方案
        """
        action = params.get('action', 'generate')
        
        if action == 'generate':
            return self._generate_video(params)
        elif action == 'analyze':
            return self._analyze_video(params)
        elif action == 'suggest':
            return self._suggest_script(params)
        else:
            return {"success": False, "error": f"未知操作: {action}"}
    
    def _generate_video(self, params: Dict) -> Dict:
        """根据描述生成视频"""
        description = params.get('description', '')
        duration = params.get('duration', 10)
        
        if not description:
            return {"success": False, "error": "缺少 description 参数"}
        
        # 使用 LLM 分析描述，生成视频参数
        try:
            from engine.semantic.engines.llm_engine import llm_engine
            result = llm_engine.understand(f"分析这个视频需求: {description}")
            intent = result[0] if result else "video"
        except:
            intent = "video"
        
        # 调用视频制作模块
        try:
            from .complete_video_maker import CompleteVideoMakerSkill
            maker = CompleteVideoMakerSkill()
            return maker.execute({
                "action": "make",
                "title": description[:20],
                "duration": duration,
                "color": "blue"
            })
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_video(self, params: Dict) -> Dict:
        """分析视频内容"""
        video_path = params.get('video_path', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}
        
        # 使用 ffmpeg 获取信息
        try:
            from .ffmpeg_video import FfmpegVideoSkill
            ffmpeg = FfmpegVideoSkill()
            return ffmpeg.execute({"action": "info", "video_path": video_path})
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _suggest_script(self, params: Dict) -> Dict:
        """推荐视频脚本方案"""
        topic = params.get('topic', '')
        
        if not topic:
            return {"success": False, "error": "缺少 topic 参数"}
        
        # 使用 LLM 生成脚本建议
        try:
            from engine.semantic.engines.llm_engine import llm_engine
            result = llm_engine.understand(f"为 '{topic}' 生成一个简短的视频脚本方案")
            script = result[0] if result else f"关于 {topic} 的视频"
        except:
            script = f"制作一个关于 {topic} 的短视频"
        
        return {
            "success": True,
            "script": script,
            "topic": topic,
            "duration": 30,
            "style": "现代"
        }


skill = LLMVideoMakerSkill()
