from skills.operation_advisor import skill as advisor
from skills.hot_dual_script import skill as script_gen
from skills.enhanced_slideshow import skill as slideshow
from skills.add_subtitles import skill as subtitle
from skills.video_uploader import skill as upload

class AutoOperatorSkill:
    name = "auto_operator"
    description = "自动运营（增强版）"
    version = "1.0.0"
    category = "operation"

    def execute(self, params):
        advice = advisor.execute({})
        suggestions = advice.get('suggestions', [])
        if not suggestions:
            return {"error": "无选题建议"}
        
        top = suggestions[0]
        topic = top.get('title', '')
        
        # 生成脚本
        scripts = script_gen.execute({'topic': topic})
        narration = scripts.get('narration', '')
        description = scripts.get('description', '')
        
        # 制作视频（多图轮播）
        video_result = slideshow.execute({
            'script': narration,
            'topic': topic,
            'output_path': 'output/enhanced.mp4'
        })
        
        # 添加字幕
        subtitle_result = subtitle.execute({
            'video_path': video_result.get('video'),
            'script': narration,
            'output_path': 'output/final.mp4'
        })
        
        # 上传
        upload_result = upload.execute({
            'video_file': subtitle_result.get('output'),
            'title': topic,
            'description': description,
            'tags': ['香港', '高才通'],
            'privacy': 'unlisted'
        })
        
        return {"success": True, "video_url": upload_result.get('video_url')}

skill = AutoOperatorSkill()
