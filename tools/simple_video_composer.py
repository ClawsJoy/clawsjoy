from lib.smart_config import smart_config

"""简单视频合成服务 - 使用 ffmpeg"""
import hashlib
import os
import subprocess


class SimpleVideoComposer:
    @staticmethod
    def compose(image_path, audio_path, output_path=None):
        """合成视频"""
        if output_path is None:
            output_path = (
                f"output/video_{hashlib.md5(image_path.encode()).hexdigest()[:8]}.mp4"
            )

        os.makedirs("output", exist_ok=True)

        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            image_path,
            "-i",
            audio_path,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            "-t",
            "30",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            return output_path
        return None


if __name__ == "__main__":
    print("视频合成服务已就绪")
