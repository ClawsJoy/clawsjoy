import re

file_path = "core/lib/v25_unified_bridge.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 __init__ 中添加 memory_file 属性
init_pattern = r'(def __init__\(self\):.*?)(\n\s+self\._local_memory = \{\})'
if re.search(init_pattern, content, re.DOTALL):
    content = re.sub(
        init_pattern,
        r'\1\n        self._memory_file = Path("data/memory.json")\n        self._memory_file.parent.mkdir(parents=True, exist_ok=True)\n        self._load_memory_from_file()\n\2',
        content,
        flags=re.DOTALL
    )

# 添加 _load_memory_from_file 和 _save_memory_to_file 方法
load_method = '''
    def _load_memory_from_file(self):
        """从文件加载记忆"""
        if self._memory_file.exists():
            try:
                with open(self._memory_file, 'r') as f:
                    self._local_memory = json.load(f)
                print(f"   ✅ 加载了 {len(self._local_memory)} 个用户的记忆")
            except Exception as e:
                print(f"   ⚠️ 加载记忆失败: {e}")
                self._local_memory = {}
        else:
            self._local_memory = {}

    def _save_memory_to_file(self):
        """保存记忆到文件"""
        try:
            with open(self._memory_file, 'w') as f:
                json.dump(self._local_memory, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"   ⚠️ 保存记忆失败: {e}")
            return False
'''

# 在 __init__ 之后插入
content = content.replace(
    'self._local_memory = {}',
    'self._local_memory = {}\n' + load_method
)

# 在 _store_local 中添加保存
store_pattern = r'(def _store_local\(self, user_id: str, key: str, value: Any\):.*?self\._local_memory\[user_id\]\[key\] = value)'
if re.search(store_pattern, content, re.DOTALL):
    content = re.sub(
        store_pattern,
        r'\1\n        self._save_memory_to_file()',
        content,
        flags=re.DOTALL
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 记忆持久化已添加")
