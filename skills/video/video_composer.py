#!/usr/bin/env python3
"""Video Composer - 视频合成技能

@version: 2.0.0
@author: ClawsJoy
@date: 2026-06-02
@enhanced: 完整实现视频合成、多轨道合并、转场效果等功能
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class VideoComposerSkill:
    """视频合成技能 - 完整版"""
    
    def __init__(self):
        self.ffmpeg_cmd = "ffmpeg"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频合成任务
        
        支持的 action:
        - compose: 合成多个视频
        - merge_audio: 合并音频到视频
        - add_transition: 添加转场效果
        - add_background_music: 添加背景音乐
        - extract_audio: 提取音频
        """
        action = params.get('action', 'compose')
        
        if action == 'compose':
            return self._compose_videos(params)
        elif action == 'merge_audio':
            return self._merge_audio(params)
        elif action == 'add_transition':
            return self._add_transition(params)
        elif action == 'add_background_music':
            return self._add_background_music(params)
        elif action == 'extract_audio':
            return self._extract_audio(params)
        else:
            return {"success": False, "error": f"未知操作: {action}"}
    
    def _compose_videos(self, params: Dict) -> Dict:
        """合成多个视频"""
        video_paths = params.get('video_paths', [])
        output_path = params.get('output', '')
        
        if not video_paths:
            return {"success": False, "error": "缺少 video_paths 参数"}
        
        if not output_path:
            output_path = f"data/output/composed_{len(video_paths)}.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 检查所有输入文件是否存在
        for vp in video_paths:
            if not Path(vp).exists():
                return {"success": False, "error": f"视频文件不存在: {vp}"}
        
        # 创建文件列表
        list_file = Path("data/temp/filelist.txt")
        list_file.parent.mkdir(parents=True, exist_ok=True)
        with open(list_file, 'w') as f:
            for vp in video_paths:
                f.write(f"file '{vp}'\n")
        
        cmd = [
            self.ffmpeg_cmd,
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            list_file.unlink()
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": f"视频合成完成，共 {len(video_paths)} 个视频",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _merge_audio(self, params: Dict) -> Dict:
        """合并音频到视频"""
        video_path = params.get('video_path', '')
        audio_path = params.get('audio_path', '')
        output_path = params.get('output', '')
        
        if not video_path or not audio_path:
            return {"success": False, "error": "缺少 video_path 或 audio_path"}
        
        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}
        
        if not Path(audio_path).exists():
            return {"success": False, "error": f"音频文件不存在: {audio_path}"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_with_audio.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "音频合并完成",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_transition(self, params: Dict) -> Dict:
        """添加转场效果"""
        video_path = params.get('video_path', '')
        transition_type = params.get('transition', 'fade')  # fade, dissolve, wipe
        output_path = params.get('output', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_transition.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 根据转场类型构建命令
        if transition_type == 'fade':
            filter_str = "fade=t=in:st=0:d=1,fade=t=out:st=4:d=1"
        elif transition_type == 'dissolve':
            filter_str = "dissolve=32"
        else:
            filter_str = "fade=t=in:st=0:d=1"
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": f"添加转场效果完成: {transition_type}",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_background_music(self, params: Dict) -> Dict:
        """添加背景音乐"""
        video_path = params.get('video_path', '')
        music_path = params.get('music_path', '')
        volume = params.get('volume', 0.3)
        output_path = params.get('output', '')
        
        if not video_path or not music_path:
            return {"success": False, "error": "缺少 video_path 或 music_path"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_bgm.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-i', music_path,
            '-filter_complex', f'[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first',
            '-c:v', 'copy',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "背景音乐添加完成",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_audio(self, params: Dict) -> Dict:
        """提取音频"""
        video_path = params.get('video_path', '')
        output_format = params.get('format', 'mp3')
        output_path = params.get('output', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_audio.{output_format}"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "音频提取完成",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = VideoComposerSkill()
