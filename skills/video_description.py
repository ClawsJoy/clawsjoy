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
