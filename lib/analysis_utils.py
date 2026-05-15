import json
from lib.memory_simple import memory

def get_latest_analysis():
    """获取最新的分析结果"""
    # 尝试多个分类
    categories = ['analysis_result', 'intelligence_analysis', 'unified_analysis']
    for cat in categories:
        items = memory.recall_all(category=cat)
        for item in reversed(items):
            try:
                return json.loads(item)
            except:
                continue
    return None
