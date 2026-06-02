#!/usr/bin/env python3
"""Ffmpeg Video - FFmpeg 视频处理技能

@version: 2.0.0
@author: ClawsJoy
@date: 2026-06-02
@enhanced: 完整实现视频信息获取、裁剪、转码、截图等功能
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class FfmpegVideoSkill:
    """FFmpeg 视频处理技能 - 完整版"""
    
    def __init__(self):
        self.ffmpeg_cmd = "ffmpeg"
        self.ffprobe_cmd = "ffprobe"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频处理任务
        
        支持的 action:
        - info: 获取视频信息
        - trim: 裁剪视频
        - transcode: 转码格式
        - screenshot: 截图
        - compose: 合成视频
        - generate: 生成测试视频
        """
        action = params.get('action', 'info')
        
        if action == 'info':
            return self._get_video_info(params)
        elif action == 'trim':
            return self._trim_video(params)
        elif action == 'transcode':
            return self._transcode_video(params)
        elif action == 'screenshot':
            return self._take_screenshot(params)
        elif action == 'compose':
            return self._compose_video(params)
        elif action == 'generate':
            return self._generate_test_video(params)
        else:
            return {"success": False, "error": f"未知操作: {action}"}
    
    def _get_video_info(self, params: Dict) -> Dict:
        """获取视频信息"""
        video_path = params.get('video_path', '')
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not Path(video_path).exists():
            return {"success": False, "error": f"视频文件不存在: {video_path}"}
        
        try:
            # 使用 ffprobe 获取视频信息
            cmd = [
                self.ffprobe_cmd,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    "success": True,
                    "info": info,
                    "size": Path(video_path).stat().st_size,
                    "message": "视频信息获取成功"
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _trim_video(self, params: Dict) -> Dict:
        """裁剪视频"""
        video_path = params.get('video_path', '')
        start_time = params.get('start', '00:00:00')
        duration = params.get('duration', 10)
        output_path = params.get('output', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_trimmed_{start_time.replace(':', '')}.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "视频裁剪完成",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _transcode_video(self, params: Dict) -> Dict:
        """转码视频格式"""
        video_path = params.get('video_path', '')
        output_format = params.get('format', 'mp4')
        output_path = params.get('output', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_converted.{output_format}"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": f"视频转码完成: {output_format}",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _take_screenshot(self, params: Dict) -> Dict:
        """截图"""
        video_path = params.get('video_path', '')
        timestamp = params.get('timestamp', '00:00:01')
        output_path = params.get('output', '')
        
        if not video_path:
            return {"success": False, "error": "缺少 video_path 参数"}
        
        if not output_path:
            name = Path(video_path).stem
            output_path = f"data/output/{name}_screenshot.jpg"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_cmd,
            '-i', video_path,
            '-ss', str(timestamp),
            '-vframes', '1',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "截图成功",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _compose_video(self, params: Dict) -> Dict:
        """合成多个视频"""
        video_paths = params.get('video_paths', [])
        output_path = params.get('output', '')
        
        if not video_paths:
            return {"success": False, "error": "缺少 video_paths 参数"}
        
        if not output_path:
            output_path = f"data/output/composed_{len(video_paths)}_videos.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
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
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_test_video(self, params: Dict) -> Dict:
        """生成测试视频（原有功能保留）"""
        output_path = params.get('output', '')
        if not output_path:
            output_path = "data/output/test_video.mp4"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        duration = params.get('duration', 5)
        color = params.get('color', 'blue')
        resolution = params.get('resolution', '1920x1080')
        
        cmd = [
            self.ffmpeg_cmd,
            '-f', 'lavfi',
            '-i', f'color=c={color}:s={resolution}:d={duration}',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and Path(output_path).exists():
                return {
                    "success": True,
                    "message": "测试视频生成完成",
                    "output": output_path,
                    "size": Path(output_path).stat().st_size
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = FfmpegVideoSkill()
