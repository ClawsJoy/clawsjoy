#!/bin/bash
# 手动添加话题到库

echo "添加新话题到本地库"
read -p "话题: " topic
read -p "分类 (tech/internet/news/ent/business): " category

cd /mnt/d/clawsjoy_clean
python3 -c "
import json
with open('data/topics/hot_topics.json', 'r') as f:
    data = json.load(f)
if '$topic' not in data['$category']:
    data['$category'].append('$topic')
    with open('data/topics/hot_topics.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print('✅ 已添加: $topic')
else:
    print('⚠️ 话题已存在')
"
