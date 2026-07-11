#!/usr/bin/env python3
"""ClawsJoy 宣传视频自动制作流水线"""

import sys
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def run_agent(agent_name, prompt, output_file):
    """运行指定 Agent 并保存输出"""
    print(f"🚀 运行 {agent_name}...")
    
    if agent_name == "video_agent_v4":
        from agents.video_agent.agent_v4 import VideoAgentV4
        agent = VideoAgentV4('promo')
    elif agent_name == "code_agent_v4":
        from agents.code_agent.agent_v4 import CodeAgentV4
        agent = CodeAgentV4('promo')
    elif agent_name == "vision_agent_v4":
        from agents.vision_agent.agent_v4 import VisionAgentV4
        agent = VisionAgentV4('promo')
    elif agent_name == "proactive_agent_v4":
        from agents.proactive_agent.agent_v4 import ProactiveAgentV4
        agent = ProactiveAgentV4('promo')
    else:
        return
    
    result = agent.process(prompt)
    with open(output_file, 'w') as f:
        f.write(result.get('response', ''))
    print(f"✅ 已保存到 {output_file}")

def main():
    print("=" * 60)
    print("🎬 ClawsJoy 宣传视频自动制作流水线")
    print("=" * 60)
    
    # 1. VideoAgent → 录屏脚本
    run_agent(
        "video_agent_v4",
        "生成 ClawsJoy 录屏脚本，展示核心功能：意图识别、多Agent协作、数据飞轮",
        "data/recording_script.md"
    )
    
    # 2. CodeAgent → FFmpeg 命令
    run_agent(
        "code_agent_v4",
        "生成 FFmpeg 录屏命令，1920x1080, 30fps, 60秒",
        "data/recording_commands.txt"
    )
    
    # 3. VisionAgent → 缩略图建议
    run_agent(
        "vision_agent_v4",
        "为 ClawsJoy 宣传视频生成缩略图建议",
        "data/thumbnail_suggestions.txt"
    )
    
    # 4. ProactiveAgent → 发布文案
    run_agent(
        "proactive_agent_v4",
        "为 ClawsJoy 宣传视频生成知乎和 GitHub 发布文案，突出本地部署、多Agent、开源",
        "data/promo_posts.md"
    )
    
    print("\n" + "=" * 60)
    print("✅ 所有内容已生成!")
    print("📁 查看 data/ 目录")
    print("🎬 运行 /tmp/auto_record.sh 开始录屏")

if __name__ == "__main__":
    main()
