#!/bin/bash
# 简单实用的学习 - 只记录真正有用的信息

LEARN_FILE="/mnt/d/clawsjoy/data/useful_knowledge.json"

# 1. 从对话中学习新关键词
echo "📚 学习新关键词..."
python3 -c "
import re
import json
from pathlib import Path
from collections import Counter

log_file = Path('/mnt/d/clawsjoy/logs/chat-api-out.log')
if log_file.exists():
    with open(log_file) as f:
        logs = f.read()
    
    # 提取用户输入
    inputs = re.findall(r'📥 处理: ([\u4e00-\u9fa5]+)', logs)
    if inputs:
        freq = Counter(inputs[-30:])
        # 只记录出现超过2次的新词
        new_words = {k:v for k,v in freq.items() if v >= 2}
        if new_words:
            print(f'发现新词: {new_words}')
            
            # 追加到学习文件
            learn_file = Path('$LEARN_FILE')
            if learn_file.exists():
                with open(learn_file) as f:
                    data = json.load(f)
            else:
                data = {'keywords': [], 'errors': [], 'tips': []}
            
            for word, count in new_words.items():
                if word not in [k['word'] for k in data['keywords']]:
                    data['keywords'].append({'word': word, 'count': count, 'learned_at': '$(date)'})
            
            with open(learn_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
"

# 2. 从错误中学习
echo "🔧 从错误中学习..."
python3 -c "
import re
import json
from pathlib import Path

error_file = Path('/mnt/d/clawsjoy/logs/system.log')
if error_file.exists():
    with open(error_file) as f:
        errors = f.read()
    
    # 提取错误类型
    error_types = re.findall(r'❌ (.*?)(?:\n|$)', errors)
    if error_types:
        from collections import Counter
        freq = Counter(error_types[-20:])
        common_errors = {k:v for k,v in freq.items() if v >= 2}
        
        if common_errors:
            print(f'常见错误: {common_errors}')
            
            learn_file = Path('$LEARN_FILE')
            if learn_file.exists():
                with open(learn_file) as f:
                    data = json.load(f)
            else:
                data = {'keywords': [], 'errors': [], 'tips': []}
            
            for err, count in common_errors.items():
                if err not in [e['error'] for e in data['errors']]:
                    data['errors'].append({'error': err[:50], 'count': count, 'last_seen': '$(date)'})
            
            with open(learn_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
"

echo "✅ 学习完成"
