#!/usr/bin/env python3
"""组装丰富内容的3分钟脚本"""

import sys
import json

def assemble_script(content, topic):
    template = f'''🎬 开场（0:00-0:20）
哈喽大家好！我是你们的香港生活博主。今天聊{topic}。
{content.get("summary", "")}

📌 核心内容（0:20-1:00）
{content.get("detail", "")}

📌 三个关键要点（1:00-2:00）
第一：{content.get("key_points", ["", "", ""])[0]}
第二：{content.get("key_points", ["", "", ""])[1]}
第三：{content.get("key_points", ["", "", ""])[2]}

📌 真实案例（2:00-2:30）
{content.get("example", "很多申请人已经成功获批")}

🎯 建议（2:30-3:00）
{content.get("advice", "分数够就赶紧递交！")}

记得点赞关注，下期见！'''
    return template

if __name__ == "__main__":
    import sys
    content_file = sys.argv[1] if len(sys.argv) > 1 else "content.json"
    topic = sys.argv[2] if len(sys.argv) > 2 else "话题"
    
    with open(content_file, 'r') as f:
        content = json.load(f)
    
    script = assemble_script(content, topic)
    print(script)
