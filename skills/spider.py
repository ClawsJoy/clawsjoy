#!/usr/bin/env python3
"""采集技能 - 从指定源采集数据"""

import json
import sys
import requests
from datetime import datetime

def execute(params):
    source = params.get('source', 'hk_news')
    limit = params.get('limit', 10)
    
    # 模拟采集不同来源
    sources = {
        "hk_news": ["香港新闻1", "香港新闻2", "香港新闻3"],
        "immd": ["入境处政策更新", "签证申请流程"],
        "hkstp": ["科技园最新动态"]
    }
    
    items = sources.get(source, sources["hk_news"])[:limit]
    
    return {
        "success": True,
        "data": items,
        "count": len(items),
        "source": source,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"source": "hk_news"}
    result = execute(input_data)
    print(json.dumps(result, ensure_ascii=False))
