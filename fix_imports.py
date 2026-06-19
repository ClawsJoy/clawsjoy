import re

file_path = "core/lib/v25_unified_bridge.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在文件开头添加必要的导入
imports = '''import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
'''

# 替换现有的导入
content = re.sub(
    r'^.*?from typing import.*?\n',
    imports,
    content,
    flags=re.DOTALL
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 导入已修复")
