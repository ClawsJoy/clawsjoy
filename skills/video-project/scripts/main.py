#!/usr/bin/env python3
"""视频剪辑项目 - 稳定版"""

import json
import subprocess
from pathlib import Path


def execute(params):
    action = params.get("action", "export")
    if action != "export":
        return {"success": False, "error": "请使用 action=export"}

    clip = params.get("clip", {})
    source = clip.get("source")
    if not source:
        return {"success": False, "error": "缺少视频源文件"}

    path = Path(source)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {source}"}

    output = params.get("output", f"downloads/{params.get('name', 'output')}.mp4")

    # 构建命令 - 使用列表形式
    cmd = ["ffmpeg", "-y", "-i", source]

    # 裁剪
    if clip.get("start", 0) > 0:
        cmd.extend(["-ss", str(clip["start"])])
    if clip.get("end"):
        duration = clip["end"] - clip.get("start", 0)
        cmd.extend(["-t", str(duration)])

    # 滤镜
    filters = clip.get("filters", {})
    if filters:
        eq_parts = []
        if filters.get("brightness"):
            eq_parts.append(f"brightness={filters['brightness']}")
        if filters.get("contrast"):
            eq_parts.append(f"contrast={filters['contrast']}")
        if filters.get("saturation"):
            eq_parts.append(f"saturation={filters['saturation']}")
        if eq_parts:
            vf = f"eq={','.join(eq_parts)}"
            cmd.extend(["-vf", vf])

    # 输出参数
    cmd.extend(
        ["-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", output]
    )

    # 调试：打印命令
    print(f"执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and Path(output).exists():
            size_mb = round(Path(output).stat().st_size / 1024 / 1024, 2)
            return {
                "success": True,
                "message": f"导出成功 ({size_mb}MB)",
                "output": output,
                "size_mb": size_mb,
            }
        return {
            "success": False,
            "error": result.stderr[:300] if result.stderr else "未知错误",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = execute(
        {
            "action": "export",
            "name": "fixed_clip",
            "clip": {
                "source": "downloads/video_1780781826.mp4",
                "start": 10,
                "end": 20,
                "filters": {"brightness": 0.1, "contrast": 1.1},
            },
            "output": "downloads/fixed_clip.mp4",
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
