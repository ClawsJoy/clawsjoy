#!/usr/bin/env python3
"""从 history.jsonl 导出 fastText 训练数据"""
import json, os

LABELS = ['greeting','identity','memory','recall','code','chat','calculate','translate']

for user_dir in os.listdir('data/users'):
    fpath = f'data/users/{user_dir}/history.jsonl'
    if not os.path.exists(fpath): continue
    with open(fpath) as f:
        for line in f:
            try:
                r = json.loads(line.strip())
                if isinstance(r, dict) and 'content' in r:
                    inner = json.loads(r['content'])
                else:
                    inner = r
                action = inner.get('action','')
                user = inner.get('user','')
                if action in LABELS and user:
                    print(f'__label__{action} {user[:200]}')
            except: pass
