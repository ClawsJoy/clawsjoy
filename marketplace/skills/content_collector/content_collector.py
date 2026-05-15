"""内容采集技能 - 标准版"""

from typing import Dict
from skills.skill_interface import BaseSkill

class ContentCollectorSkill(BaseSkill):
    name = "content_collector"
    description = "从互联网采集新闻、热点和内容"
    version = "1.0.0"
    category = "content"
    
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["search", "trending"]},
            "keyword": {"type": "string"},
            "limit": {"type": "integer", "default": 10}
        },
        "required": ["action"]
    }
    
    output_schema = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "results": {"type": "array"},
            "count": {"type": "integer"}
        }
    }
    
    def execute(self, params: Dict) -> Dict:
        from .content.real_collector import real_collector
        return real_collector.execute(params)

# 注册实例
skill = ContentCollectorSkill()
    # 添加更简单的调用方式
    def execute(self, params: Dict) -> Dict:
        # 兼容两种调用方式
        if 'action' not in params:
            # 如果是简单调用，默认为搜索
            keyword = params.get('keyword', params.get('topic', ''))
            if keyword:
                params = {'action': 'search', 'keyword': keyword, 'limit': 5}
            else:
                params = {'action': 'trending', 'limit': 5}
        
        from .content.real_collector import real_collector
        return real_collector.execute(params)
