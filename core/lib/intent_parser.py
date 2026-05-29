from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""自然语言意图解析器 - 增强版"""

class IntentParser:
    INTENT_PATTERNS = {
        "视频制作": {
            "keywords": ["视频", "漫剧", "制作", "生成视频", "做视频"],
            "skills": ["manju_maker", "complete_video_maker"]
        },
        "数学计算": {
            "keywords": ["计算", "加法", "乘法", "统计", "加", "减", "乘", "除"],
            "skills": ["add", "multiply", "statistics"]
        },
        "文本处理": {
            "keywords": ["大小写", "反转", "文字", "字符串", "文本"],
            "skills": ["to_upper", "reverse", "count_words"]
        },
        "日程管理": {
            "keywords": ["提醒", "日程", "会议", "待办", "任务", "计划"],
            "skills": ["add_event", "set_reminder", "add_todo"]
        },
        "视频上传": {
            "keywords": ["上传", "发布", "分享视频"],
            "skills": ["video_uploader"]
        },
        "添加字幕": {
            "keywords": ["字幕", "添加字幕", "加字幕"],
            "skills": ["add_subtitles"]
        }
    }
    
    @classmethod
    def parse(cls, user_input: str) -> dict:
        user_input_lower = user_input.lower()
        
        # 按优先级匹配
        for intent, config in cls.INTENT_PATTERNS.items():
            for keyword in config["keywords"]:
                if keyword in user_input_lower:
                    return {
                        "intent": intent,
                        "skills": config["skills"],
                        "confidence": 1.0,
                        "message": f"识别到{intent}意图"
                    }
        
        # 默认返回
        return {
            "intent": "general",
            "skills": ["get_time"],
            "confidence": 0.3,
            "message": "未识别明确意图，执行默认操作"
        }
    
    @classmethod
    def get_intent(cls, user_input: str) -> str:
        return cls.parse(user_input)["intent"]

intent_parser = IntentParser()
