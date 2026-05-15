#!/usr/bin/env python3
"""让大脑按 Workspace 配置执行第二集生成"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/mnt/d/clawsjoy')

# 1. 读取 Workspace 配置
workspace = Path('/mnt/d/clawsjoy/experiments/youtube_series/workspace')
memory_file = workspace / 'MEMORY.md'

print("="*60)
print("🎬 香港故事连续剧 - 第二集生成")
print("="*60)

# 读取项目记忆
memory_content = memory_file.read_text(encoding='utf-8') if memory_file.exists() else ""
print(f"\n📖 读取项目记忆:\n{memory_content[:300]}...")

# 提取前情提要
prev_summary = ""
if "第一集摘要" in memory_content:
    import re
    match = re.search(r"第一集摘要\n(.+?)\n\n", memory_content)
    if match:
        prev_summary = match.group(1)

print(f"\n📜 前情提要: {prev_summary}")

# 2. 调用 story_outline
print("\n📝 正在生成故事大纲...")
from skills.story_outline import skill as outline_skill

outline_result = outline_skill.execute({
    "topic": "香港优才计划",
    "style": "叙事性强，情感丰富",
    "duration_minutes": 3,
    "episode": 2,
    "memory_context": prev_summary
})

if not outline_result.get('success'):
    print(f"❌ 大纲生成失败: {outline_result.get('error')}")
    sys.exit(1)

outline = outline_result['outline']
print(f"\n✅ 大纲生成成功")
print(f"   标题: {outline.get('title')}")
print(f"   梗概: {outline.get('logline')}")

# 3. 生成完整脚本
print("\n✍️ 正在生成脚本...")

script_prompt = f"""根据以下大纲生成完整的3分钟旁白稿：

标题：{outline.get('title')}
梗概：{outline.get('logline')}

分幕：
{json.dumps(outline.get('acts'), ensure_ascii=False, indent=2)}

要求：
- 只输出旁白内容，不要【】等标记
- 不要角色名加冒号
- 直接写描述性文字和对白
- 时长3分钟，约600字
"""

import requests
resp = requests.post("http://localhost:11434/api/generate",
                     json={"model": "qwen2.5:7b", "prompt": script_prompt, "stream": False},
                     timeout=120)

script = resp.json().get('response', '')
print(f"\n✅ 脚本生成，长度: {len(script)} 字符")

# 保存脚本
output_file = workspace / 'episode_2_script.txt'
output_file.write_text(script, encoding='utf-8')
print(f"💾 脚本已保存: {output_file}")

# 4. 下一步建议
print("\n" + "="*60)
print("🎯 下一步（可让大脑继续执行）：")
print("   1. TTS 转语音")
print("   2. video_maker 合成视频")
print("   3. whisper_transcribe 学习内容")
print("="*60)

# 5. 记录执行日志
from datetime import datetime
log_file = workspace / 'memory' / f'{datetime.now().strftime("%Y-%m-%d")}.md'
log_file.parent.mkdir(exist_ok=True)

log_entry = f"""
## 第二集生成 - {datetime.now().strftime("%H:%M:%S")}

- 大纲标题: {outline.get('title')}
- 脚本长度: {len(script)} 字符
- 状态: ✅ 成功

### 大纲详情
{json.dumps(outline, ensure_ascii=False, indent=2)[:500]}

### 脚本预览
{script[:200]}...
"""

log_file.write_text(log_entry, encoding='utf-8') if not log_file.exists() else \
    log_file.write_text(log_file.read_text(encoding='utf-8') + log_entry, encoding='utf-8')

print(f"📋 执行日志已记录: {log_file}")
