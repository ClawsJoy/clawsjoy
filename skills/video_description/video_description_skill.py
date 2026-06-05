"""技能实现"""


class VideoDescription:
    name = "video_description"
    description = "video_description 技能"
    version = "1.0.0"

    def execute(self, params):
        return {"success": True, "result": f"video_description 执行成功"}
