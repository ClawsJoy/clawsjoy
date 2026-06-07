#!/usr/bin/env python3
"""自学习视频处理 - 根据反馈自动调整"""

import json
import re
import subprocess
import sys
from pathlib import Path


class VideoLearnSkill:
    name = "video-learn"
    description = "自学习视频处理"
    version = "1.0.0"

    # 反馈到参数的映射（可学习更新）
    FEEDBACK_MAP = {
        "太暗": {"brightness": 0.1, "contrast": 0.05},
        "太亮": {"brightness": -0.1, "contrast": -0.05},
        "模糊": {"sharpness": 1.2, "unsharp": "5:5:1.0"},
        "颜色太淡": {"saturation": 1.2},
        "颜色太浓": {"saturation": 0.8},
        "对比度不够": {"contrast": 0.15},
        "太冷": {"color_temp": "warm"},
        "太暖": {"color_temp": "cool"},
    }

    def __init__(self):
        self.learning_memory = {}  # 存储学习历史

    def execute(self, params):
        video_path = params.get("video_path", "")
        feedback = params.get("feedback", "")

        if not video_path or not feedback:
            return {"success": False, "error": "需要 video_path 和 feedback"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 1. 理解反馈
        adjustments = self._understand_feedback(feedback)

        # 2. 应用调整
        result = self._apply_adjustments(path, adjustments)

        # 3. 记录学习
        self._record_learning(feedback, adjustments, result)

        return {
            "success": True,
            "original": video_path,
            "adjusted": result.get("output"),
            "feedback_understood": adjustments,
            "learning_id": len(self.learning_memory),
        }

    def _understand_feedback(self, feedback):
        """理解自然语言反馈，映射到参数调整"""
        adjustments = {}

        for keyword, params in self.FEEDBACK_MAP.items():
            if keyword in feedback:
                adjustments.update(params)

        # 提取数值（如 "亮一点" → +0.05）
        if "一点" in feedback or "稍微" in feedback:
            for key in adjustments:
                adjustments[key] = adjustments.get(key, 0) * 0.5

        if "很多" in feedback or "非常" in feedback:
            for key in adjustments:
                adjustments[key] = adjustments.get(key, 0) * 1.5

        return adjustments

    def _apply_adjustments(self, path, adjustments):
        """应用参数调整到视频"""
        if not adjustments:
            return {"output": str(path), "no_change": True}

        output_path = path.parent / f"{path.stem}_adjusted.mp4"

        # 构建 ffmpeg 滤镜
        filters = []
        if "brightness" in adjustments:
            filters.append(f"eq=brightness={adjustments['brightness']}")
        if "contrast" in adjustments:
            filters.append(f"eq=contrast={adjustments['contrast']}")
        if "saturation" in adjustments:
            filters.append(f"eq=saturation={adjustments['saturation']}")
        if "sharpness" in adjustments:
            filters.append(f"unsharp=5:5:{adjustments['sharpness']}:5:5:0")

        if filters:
            filter_str = ",".join(filters)
            cmd = [
                "ffmpeg",
                "-i",
                str(path),
                "-vf",
                filter_str,
                "-c:a",
                "copy",
                "-y",
                str(output_path),
            ]
            subprocess.run(cmd, capture_output=True)
            return {"output": str(output_path)}

        return {"output": str(path)}

    def _record_learning(self, feedback, adjustments, result):
        """记录学习经验"""
        learning_id = len(self.learning_memory)
        self.learning_memory[learning_id] = {
            "feedback": feedback,
            "adjustments": adjustments,
            "result": result.get("output"),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoLearnSkill()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))
