#!/usr/bin/env python3
"""从内容库组装3分钟视频脚本"""

import json
import sys
import random

def load_library():
    with open('topics_library.json', 'r') as f:
        return json.load(f)

def get_random_topic(library):
    topics = list(library.keys())
    return random.choice(topics)

def assemble_script(topic, library):
    data = library.get(topic, {})
    
    script = f'''🎬 开场（0:00-0:25）
{data.get("开场", "今天聊聊"+topic)}

📌 第一个要点（0:25-1:00）
{data.get("要点1", "政策内容")}

📌 第二个要点（1:00-1:35）
{data.get("要点2", "申请条件")}

📌 第三个要点（1:35-2:10）
{data.get("要点3", "注意事项")}

📌 真实案例（2:10-2:30）
{data.get("案例", "成功案例")}

🎯 建议（2:30-2:50）
{data.get("建议", "实用建议")}

🎬 结尾（2:50-3:00）
{data.get("结尾", "点赞关注下期见")}'''
    
    return script

if __name__ == "__main__":
    library = load_library()
    topic = sys.argv[1] if len(sys.argv) > 1 else get_random_topic(library)
    script = assemble_script(topic, library)
    
    # 保存脚本
    with open(f"output/scripts/{topic}.txt", "w") as f:
        f.write(script)
    
    print(json.dumps({
        "topic": topic, 
        "script": script,
        "success": True
    }, ensure_ascii=False))
