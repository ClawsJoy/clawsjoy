import re

file_path = "core/lib/redis_manager.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 _init 方法：直接从 yaml 文件读取配置
old_init = '''    def _init(self):
        config_file = Path(__file__).parent.parent / "config/cache/redis.yaml"
        if config_file.exists():
            with open(config_file) as f:
                self._config = unified_config.get("redis_manager", {}).get("redis", {})
        else:
            self._config = {"enabled": False}

        if self._config.get("enabled", False):'''

new_init = '''    def _init(self):
        config_file = Path(__file__).parent.parent / "config/cache/redis.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                self._config = data.get("redis", {})
                # 如果配置中没有 enabled 字段，默认启用
                if "enabled" not in self._config:
                    self._config["enabled"] = True
        else:
            self._config = {"enabled": False}

        if self._config.get("enabled", False):'''

content = content.replace(old_init, new_init)

# 确保 yaml 已导入
if 'import yaml' not in content:
    content = content.replace('import redis', 'import redis\nimport yaml')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ redis_manager.py 已修复")
print("   - 直接从 config/cache/redis.yaml 读取配置")
print("   - 不再依赖 unified_config")
