import re
from pathlib import Path

# 需要修复的文件
files_to_fix = [
    'agents/core/autonomous_learner.py',
    'agents/core/reflection_engine.py',
    'agents/core/simple_learning_agent.py',
    'agents/core/tenant_agent.py',
    'agents/core/true_intelligence_light.py',
    'agents/core/true_intelligence_v2.py',
    'agent_core/brain_connector.py',
]

config_line = 'from lib.unified_config import config\n'

for file_path in files_to_fix:
    p = Path(file_path)
    if not p.exists():
        continue
    
    content = p.read_text()
    
    # 添加导入
    if 'from lib.unified_config' not in content and 'from lib.unified_config import config' not in content:
        content = config_line + content
    
    # 替换硬编码模型名
    content = re.sub(r'"qwen2.5:7b"', 'config.LLM["default_model"]', content)
    content = re.sub(r"'qwen2.5:7b'", 'config.LLM["default_model"]', content)
    content = re.sub(r'"qwen2.5:3b"', 'config.LLM["fast_model"]', content)
    content = re.sub(r"'qwen2.5:3b'", 'config.LLM["fast_model"]', content)
    
    p.write_text(content)
    print(f"✅ 修复: {file_path}")

print("\n✅ 模型名修复完成")
