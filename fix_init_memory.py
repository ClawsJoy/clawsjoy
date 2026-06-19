import re

file_path = "core/lib/v25_unified_bridge.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 __init__ 方法
old_init = '''    def __init__(self):
        print("🌉 2.5 层 JSON 统一桥梁初始化")
        self._memory = None
        self._capability_loader = None
        self._evaluator = None
        self._recommender = None'''

new_init = '''    def __init__(self):
        print("🌉 2.5 层 JSON 统一桥梁初始化")
        self._memory = None
        self._capability_loader = None
        self._evaluator = None
        self._recommender = None
        self._local_memory = {}
        self._memory_file = Path("data/memory.json")
        self._memory_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_memory_from_file()'''

content = content.replace(old_init, new_init)

# 添加 _load_memory_from_file 方法（如果不存在）
if '_load_memory_from_file' not in content:
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
'''
    content = content.replace('def _save_memory_to_file(self):', load_method + '\n    def _save_memory_to_file(self):')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ __init__ 已修复")
