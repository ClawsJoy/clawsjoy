#!/usr/bin/env python3
"""内容写作技能"""

import json
import sys

def execute(params):
    topic = params.get('topic', '香港')
    style = params.get('style', '专业')
    
    # 尝试从上游获取数据
    step_results = params.get('_step_results', {})
    merged_data = step_results.get('merge_data', {}).get('output', {})
    items = merged_data.get('data', []) if isinstance(merged_data, dict) else []
    
    if items:
        content = f"今日{len(items)}条热点：\n" + "\n".join(f"- {item}" for item in items[:5])
    else:
        content = f"{topic}{style}相关内容。"
    
    script = f"""【{style}风格】{topic}相关资讯。

{content}

关注我们获取更多{topic}资讯。"""
    
    return {
        "success": True,
        "script": script,
        "topic": topic,
        "word_count": len(script),
        "items_used": len(items)
    }

if __name__ == "__main__":
    data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    result = execute(data)
    print(json.dumps(result, ensure_ascii=False))
