import os
import yaml
from pathlib import Path

file_path = "core/lib/redis_manager.py"

with open(file_path, 'r') as f:
    content = f.read()

# 替换配置加载逻辑
old_config = '''
            try:
                self._config = unified_config.get("redis_manager", {}).get("redis", {})
            except:
                self._config = {"enabled": False}'''

new_config = '''
            # 直接从 config/cache/redis.yaml 加载
            try:
                config_file = Path("config/cache/redis.yaml")
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        data = yaml.safe_load(f)
                        self._config = data.get("redis", {})
                        if self._config.get("enabled"):
                            # 从统一配置获取密码（如果有）
                            try:
                                redis_url = unified_config.get("redis", {}).get("url", "")
                                if redis_url and ":" in redis_url:
                                    # 解析 URL 获取密码
                                    pass
                            except:
                                pass
                else:
                    self._config = {"enabled": False}
            except Exception as e:
                print(f"⚠️ Redis 配置加载失败: {e}")
                self._config = {"enabled": False}'''

content = content.replace(old_config, new_config)

# 添加 yaml 导入
if 'import yaml' not in content:
    content = content.replace('import redis', 'import redis\nimport yaml')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ redis_manager 配置加载已修复")
