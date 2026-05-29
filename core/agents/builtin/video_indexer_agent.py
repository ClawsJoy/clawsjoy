"""视频索引 Agent - 提取关键帧并生成描述"""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from core.agents.base.smart_agent import SmartAgent


class VideoIndexerAgent(SmartAgent):
    """视频索引 Agent"""

    name = "video_indexer_agent"
    description = "视频关键帧提取和描述生成"
    version = "1.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._init_vision_skill()
        print("🎬 VideoIndexerAgent 初始化完成")

    def _init_vision_skill(self):
        """初始化视觉技能"""
        try:
            from skills.image.vision import VisionSkill
            self.vision_skill = VisionSkill()
            print("   ✅ 视觉技能已加载")
        except Exception as e:
            print(f"   ❌ 技能加载失败: {e}")
            self.vision_skill = None

    def extract_frames(self, video_path: str, interval: int = 10, max_frames: int = 5) -> List[str]:
        """提取视频关键帧"""
        frames = []
        try:
            # 获取视频时长
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip())

            # 计算帧间隔
            step = duration / (max_frames + 1)

            with tempfile.TemporaryDirectory() as tmpdir:
                for i in range(max_frames):
                    timestamp = step * (i + 1)
                    frame_path = Path(tmpdir) / f"frame_{i}.jpg"
                    
                    subprocess.run([
                        'ffmpeg', '-ss', str(timestamp), '-i', video_path,
                        '-vframes', '1', '-q:v', '2', str(frame_path)
                    ], capture_output=True)
                    
                    if frame_path.exists():
                        frames.append(str(frame_path))
        except Exception as e:
            print(f"   ⚠️ 帧提取失败: {e}")

        return frames

    def describe_video(self, video_path: str) -> Dict:
        """描述视频内容"""
        if not self.vision_skill:
            return {"success": False, "error": "Vision skill not available"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"Video not found: {video_path}"}

        # 提取关键帧
        frames = self.extract_frames(video_path)

        if not frames:
            return {
                "success": True,
                "description": f"视频文件: {path.name} (无法提取帧)",
                "frames_analyzed": 0
            }

        # 分析每一帧
        descriptions = []
        for frame_path in frames:
            result = self.vision_skill.execute({
                "image_path": frame_path,
                "prompt": "描述这张视频画面"
            })
            if result.get('success'):
                descriptions.append(result.get('description', ''))

        # 获取视频元数据
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip()) if result.stdout else 0

            result2 = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                 '-show_entries', 'stream=width,height', 
                 '-of', 'default=noprint_wrappers=1', video_path],
                capture_output=True, text=True
            )
            resolution = result2.stdout.strip().replace('\n', 'x')
        except:
            duration = 0
            resolution = "unknown"

        # 合并描述
        combined = f"视频: {path.name}\n时长: {duration:.1f}秒\n分辨率: {resolution}\n"
        if descriptions:
            combined += f"画面描述: {' '.join(descriptions[:3])}"

        return {
            "success": True,
            "description": combined,
            "frames_analyzed": len(frames),
            "duration": duration,
            "resolution": resolution
        }


video_indexer = VideoIndexerAgent()
