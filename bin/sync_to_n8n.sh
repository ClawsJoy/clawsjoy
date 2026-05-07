#!/bin/bash
# 自动将 workflows/*.json 同步到 n8n
cd /mnt/d/clawsjoy
python3 -c "
import json
from pathlib import Path
wf_dir = Path('workflows')
out_dir = Path('data/n8n/import')
out_dir.mkdir(parents=True, exist_ok=True)
for f in wf_dir.glob('*.json'):
    with open(f) as src:
        wf = json.load(src)
    # 简化转换
    n8n_wf = {
        'name': f.stem,
        'nodes': [{
            'name': step.get('name', step.get('skill')),
            'type': 'n8n-nodes-base.httpRequest',
            'parameters': {
                'url': 'http://host.docker.internal:8108/api/promo/make',
                'method': 'POST',
                'sendBody': True,
                'bodyParameters': step.get('params', {})
            }
        } for step in wf.get('steps', [])]
    }
    with open(out_dir / f.name, 'w') as dst:
        json.dump(n8n_wf, dst, indent=2)
print('✅ 工作流已同步到 n8n 导入目录')
"
