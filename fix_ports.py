import re
from pathlib import Path

# 需要修复的文件列表
files_to_fix = [
    'agents/core/agent_api.py',
    'agents/core/promo_api.py',
    'agents/core/tenant_agent.py',
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
    
    # 替换端口硬编码
    content = re.sub(r'port=5002', 'port=config.get_port("gateway")', content)
    content = re.sub(r'port=5003', 'port=config.get_port("file")', content)
    content = re.sub(r'port=5005', 'port=config.get_port("multi_agent")', content)
    content = re.sub(r'port=5008', 'port=config.get_port("doc")', content)
    content = re.sub(r'port=5010', 'port=config.get_port("agent_api")', content)
    content = re.sub(r'port=5011', 'port=config.get_port("web")', content)
    
    p.write_text(content)
    print(f"✅ 修复: {file_path}")

print("\n✅ 端口修复完成")
