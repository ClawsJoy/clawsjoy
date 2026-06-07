"""从视频中提取关键帧"""

import os
import subprocess
from pathlib import Path


def extract_frames(video_path, output_dir=None, num_frames=5):
    """提取视频中的关键帧"""
    video_path = Path(video_path)
    if not video_path.exists():
        return {"error": "视频文件不存在"}

    if output_dir is None:
        output_dir = Path("/tmp/frames") / video_path.stem
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取视频时长
    cmd_duration = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd_duration, capture_output=True, text=True)
    duration = float(result.stdout.strip()) if result.stdout else 0

    # 计算帧位置
    frames = []
    for i in range(num_frames):
        position = (i + 1) * duration / (num_frames + 1)
        output_path = output_dir / f"frame_{i+1}_{int(position)}s.jpg"

        cmd = [
            "ffmpeg",
            "-ss",
            str(position),
            "-i",
            str(video_path),
            "-vframes",
            "1",
            "-q:v",
            "2",
            "-y",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True)
        frames.append(str(output_path))

    return {"frames": frames, "duration": duration, "frame_count": len(frames)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = extract_frames(sys.argv[1])
        print(result)
