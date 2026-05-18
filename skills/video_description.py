import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.smart_config import smart_config
from lib.memory_simple import memory

class VideoDescriptionSkill:
    name = "video_description"

    def execute(self, params):
        title = params.get("title", "")
        script = params.get("script", "")  # 接收脚本内容
        tags = params.get("tags", [])

        # 从脚本生成摘要（取前 200 字）
        summary = script[:200] if script else title
        description = f"{summary}\n\n[AI Generated] This video is created by AI technology."

        memory.remember(
            f"video_meta:{title}|desc:{description}|tags:{','.join(tags)}",
            category="video_metadata"
        )

        return {
            "success": True,
            "title": title,
            "description": description,
            "tags": tags
        }

skill = VideoDescriptionSkill()
