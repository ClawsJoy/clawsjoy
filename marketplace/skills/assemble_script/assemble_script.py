#!/usr/bin/env python3
"""将AI提取的内容组装成3分钟脚本"""

import sys
import json

def assemble_script(content, topic):
    template = f'''🎬 开场（0:00-0:20）
哈喽大家好！今天我们来聊一个超重磅的话题——{topic}。
很多朋友都在问，今天3分钟给你讲清楚，全是干货！

📌 核心内容（0:20-1:00）
{content.get("summary", "")}

📌 三个关键要点（1:00-2:00）
第一：{content.get("key_points", [""])[0] if len(content.get("key_points", [])) > 0 else ""}
第二：{content.get("key_points", [""])[1] if len(content.get("key_points", [])) > 1 else ""}
第三：{content.get("key_points", [""])[2] if len(content.get("key_points", [])) > 2 else ""}

📌 真实案例（2:00-2:30）
{content.get("example", "很多申请人已经成功获批")}

🎯 给你们的建议（2:30-3:00）
{content.get("advice", "分数够就赶紧递交！")}

最后，如果觉得有用，记得点赞关注！评论区告诉我你的分数，帮你评估。'''
    return template

if __name__ == "__main__":
    import sys
    content_file = sys.argv[1] if len(sys.argv) > 1 else "content.json"
    topic = sys.argv[2] if len(sys.argv) > 2 else "话题"
    
    with open(content_file, 'r') as f:
        content = json.load(f)
    
    script = assemble_script(content, topic)
    print(script)
