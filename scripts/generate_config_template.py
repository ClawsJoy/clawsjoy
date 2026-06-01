#!/usr/bin/env python3
"""生成引擎配置模板"""

from pathlib import Path

TEMPLATE = '''# {name} 引擎配置
# 自动生成，请根据实际情况修改

version: "1.0.0"

engine:
  name: {name}
  enabled: true
  log_level: "INFO"
  timeout: 30
  retry_count: 3

# 引擎特定配置
settings:
  # 在此添加引擎特定配置
  pass
'''

def generate_configs():
    engine_dir = Path("engine")
    config_dir = Path("config/engines")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    generated = []
    for subdir in engine_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('_'):
            if subdir.name in ['base', 'lib', 'events', 'generator', 'workflows', 'market']:
                continue
            
            config_file = config_dir / f"{subdir.name}.yaml"
            if not config_file.exists():
                config_file.write_text(TEMPLATE.format(name=subdir.name))
                generated.append(subdir.name)
    
    print(f"✅ 生成 {len(generated)} 个配置模板: {generated}")

if __name__ == "__main__":
    generate_configs()
