from lib.smart_config import smart_config
import re
from pathlib import Path

# 需要修复的文件
files_to_fix = [
    'agents/core/adaptive_tuner.py',
    'agents/core/autonomous_learner.py',
    'agents/core/event_monitor.py',
    'agents/core/reflection_engine.py',
    'agents/core/true_intelligence_light.py',
    'agents/core/true_intelligence_v2.py',
]

config_line = 'from lib.unified_config import config\n'

for file_path in files_to_fix:
    p = Path(file_path)
    if not p.exists():
        continue
    
    content = p.read_text()
    
    # 添加导入
    if 'from lib.unified_config' not in content:
        content = config_line + content
    
    # 替换 localhost:str(smart_config.get_port("gateway"))
    content = re.sub(r"'http://smart_config.HOST:str(smart_config.get_port("gateway"))'", 'ff"{smart_config.get_service_url("{config.get_port("gateway")}"', content)
    content = re.sub(r'"http://smart_config.HOST:str(smart_config.get_port("gateway"))"', 'ff"{smart_config.get_service_url("{config.get_port("gateway")}"', content)
    
    # 替换 localhost:str(smart_config.get_port("ollama"))
    content = re.sub(r"'http://smart_config.HOST:str(smart_config.get_port("ollama"))'", 'config.LLM["ollama_endpoint"]', content)
    content = re.sub(r'"http://smart_config.HOST:str(smart_config.get_port("ollama"))"', 'config.LLM["ollama_endpoint"]', content)
    
    p.write_text(content)
    print(f"✅ 修复: {file_path}")

print("\n✅ URL 修复完成")
