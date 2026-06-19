import re

file_path = "core/lib/redis_manager.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 __init__ 最后强制设置 enabled
init_pattern = r'(def __init__\(self\).*?)(\n\s+if self\._config\.get\("enabled"\):)'

def add_force(match):
    before = match.group(1)
    rest = match.group(2)
    force_code = '''
        # 🔧 强制启用 Redis（如果配置了 host 和 port）
        if self._config.get("host") and self._config.get("port"):
            if not self._config.get("enabled", False):
                print("🔧 强制启用 Redis（配置存在）")
                self._config["enabled"] = True
'''
    return before + force_code + '\n' + rest

# 如果上面的替换不工作，直接在文件末尾的 else 之前插入
content = re.sub(
    r'(else:\s+print\("ℹ️ Redis 未启用，使用文件存储"\)\s+self\._config\s*=\s*{"enabled":\s*False})',
    r'''else:
                # 检查是否有 host 和 port 配置，如果有则强制启用
                if self._config.get("host") and self._config.get("port"):
                    print("🔧 强制启用 Redis（配置存在）")
                    self._config["enabled"] = True
                else:
                    print("ℹ️ Redis 未启用，使用文件存储")
                    self._config = {"enabled": False}''',
    content,
    flags=re.DOTALL
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ redis_manager 强制启用已添加")
