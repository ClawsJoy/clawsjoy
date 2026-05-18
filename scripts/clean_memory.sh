#!/bin/bash
# 清理记忆中的失败记录

cd /mnt/d/clawsjoy

python3 << 'PYEOF'
import json
from datetime import datetime, timedelta

# 清理工作流失败记录
with open('data/memory_simple.json', 'r') as f:
    data = json.load(f)

# 只保留成功记录
if 'workflow_outcome' in data['categories']:
    data['categories']['workflow_outcome'] = [
        item for item in data['categories']['workflow_outcome'] 
        if '成功' in item or '摘要' in item
    ]

# 清理 items
data['items'] = [
    item for item in data['items'] 
    if item.get('category') != 'workflow_outcome' or '成功' in item.get('fact', '') or '摘要' in item.get('fact', '')
]

with open('data/memory_simple.json', 'w') as f:
    json.dump(data, f, indent=2)

print('✅ 记忆清理完成')
PYEOF
