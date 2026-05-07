#!/usr/bin/env python3
"""生成3分钟完整YouTube脚本"""

import requests
import json

def generate_full_script(topic):
    prompt = f"""你是一个百万粉丝的YouTube香港生活博主。请写一个**完整的3分钟视频脚本**。

主题：{topic}

【脚本格式要求】
总时长：180秒（3分钟）

🎬 开场白（0:00-0:20）20秒：
- 抓人眼球的Hook
- 本期价值预告
- 个人IP介绍

📌 第一部分：核心政策解读（0:20-1:00）40秒：
- 政策背景
- 关键变化
- 具体内容

📌 第二部分：申请条件分析（1:00-1:40）40秒：
- 硬性条件
- 加分项
- 常见误区

📌 第三部分：实操建议（1:40-2:20）40秒：
- 准备材料
- 申请流程
- 时间节点

📌 第四部分：成功案例（2:20-2:40）20秒：
- 具体案例
- 经验分享

🎯 结尾（2:40-3:00）20秒：
- 总结核心观点
- 互动引导
- 下期预告

【风格要求】
- 完全口语化，像和好朋友聊天
- 每句话15-25字，节奏快
- 使用“划重点”、“干货来了”、“注意了”等词
- 适当使用问句和感叹句

【输出要求】
完整输出脚本，每段标注时长，不要解释。"""

    resp = requests.post("http://localhost:8101/api/agent",
        json={"text": prompt}, timeout=120)
    
    if resp.status_code == 200:
        return resp.json().get("message", "")
    return ""

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划2026"
    script = generate_full_script(topic)
    print(script)
    # 同时也保存到文件
    with open(f"output/scripts/3min_{topic[:20]}.txt", "w") as f:
        f.write(script)
    print(f"\n✅ 脚本已保存到 output/scripts/3min_{topic[:20]}.txt")
