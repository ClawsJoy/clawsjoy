#!/bin/bash
echo "🎬 ClawsJoy 宣传视频内容生成器"
echo "================================="

cd /home/flybo/clawsjoy_v5

# 1. 生成脚本
echo "📋 1. DirectorAgent 生成脚本..."
python -c "
import sys
sys.path.insert(0, '.')
from agents.director_agent.agent_v4 import DirectorAgentV4
agent = DirectorAgentV4('promo')
result = agent.process('制作 ClawsJoy 宣传视频，展示多 Agent 协作和本地部署优势')
with open('data/promo_script.md', 'w') as f:
    f.write(result.get('response', ''))
print('✅ 脚本已保存')
"

# 2. 生成旁白
echo "🎙️ 2. WriterAgent 生成旁白..."
python -c "
import sys
sys.path.insert(0, '.')
from agents.writer_agent.agent_v4 import WriterAgentV4
script = open('data/promo_script.md').read()[:2000]
agent = WriterAgentV4('promo')
result = agent.process(f'优化以下旁白：\n{script}')
with open('data/promo_narration.txt', 'w') as f:
    f.write(result.get('response', ''))
print('✅ 旁白已保存')
"

# 3. 生成视频命令
echo "💻 3. CodeAgent 生成视频命令..."
python -c "
import sys
sys.path.insert(0, '.')
from agents.code_agent.agent_v4 import CodeAgentV4
agent = CodeAgentV4('promo')
result = agent.process('生成 FFmpeg 命令，把截图合成 1920x1080 宣传视频，每图3秒，淡入淡出')
with open('data/promo_commands.txt', 'w') as f:
    f.write(result.get('response', ''))
print('✅ 命令已保存')
"

# 4. 生成描述
echo "🎬 4. VideoAgent 生成描述..."
python -c "
import sys
sys.path.insert(0, '.')
from agents.video_agent.agent_v4 import VideoAgentV4
agent = VideoAgentV4('promo')
result = agent.process('为 ClawsJoy 宣传视频生成描述和标签')
with open('data/promo_description.txt', 'w') as f:
    f.write(result.get('response', ''))
print('✅ 描述已保存')
"

echo ""
echo "✅ 所有内容已生成！"
echo "📁 查看: cat data/promo_*.md data/promo_*.txt"
