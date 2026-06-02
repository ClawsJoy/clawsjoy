#!/usr/bin/env python3
"""Video Skill - 视频处理统一入口

@version: 2.0.0
@author: ClawsJoy
@date: 2026-06-02
"""

from typing import Dict, Any


class VideoSkill:
    """视频处理技能 - 统一入口"""
    
    def __init__(self):
        self._modules = {}
        self._load_modules()
    
    def _load_modules(self):
        """加载子模块"""
        try:
            from .ffmpeg_video import FfmpegVideoSkill
            self._modules['ffmpeg'] = FfmpegVideoSkill()
        except:
            pass
        
        try:
            from .video_composer import VideoComposerSkill
            self._modules['composer'] = VideoComposerSkill()
        except:
            pass
        
        try:
            from .complete_video_maker import CompleteVideoMakerSkill
            self._modules['maker'] = CompleteVideoMakerSkill()
        except:
            pass
        
        try:
            from .add_subtitles import AddSubtitlesSkill
            self._modules['subtitle'] = AddSubtitlesSkill()
        except:
            pass
        
        try:
            from .manju_maker import ManjuMakerSkill
            self._modules['manju'] = ManjuMakerSkill()
        except:
            pass
        
        try:
            from .video_uploader import VideoUploaderSkill
            self._modules['uploader'] = VideoUploaderSkill()
        except:
            pass
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频处理任务
        
        支持的 action:
        - ffmpeg: FFmpeg 基础操作
        - compose: 视频合成
        - make: 完整制作
        - subtitle: 添加字幕
        - manju: 漫剧生成
        - upload: 视频上传
        """
        action = params.get('action', 'ffmpeg')
        
        if action == 'ffmpeg' and 'ffmpeg' in self._modules:
            return self._modules['ffmpeg'].execute(params)
        elif action == 'compose' and 'composer' in self._modules:
            return self._modules['composer'].execute(params)
        elif action == 'make' and 'maker' in self._modules:
            return self._modules['maker'].execute(params)
        elif action == 'subtitle' and 'subtitle' in self._modules:
            return self._modules['subtitle'].execute(params)
        elif action == 'manju' and 'manju' in self._modules:
            return self._modules['manju'].execute(params)
        elif action == 'upload' and 'uploader' in self._modules:
            return self._modules['uploader'].execute(params)
        else:
            return {"success": False, "error": f"未知操作或模块不可用: {action}"}
    
    def get_actions(self) -> list:
        """获取可用操作列表"""
        return list(self._modules.keys())


skill = VideoSkill()
