#!/usr/bin/env python3
"""n8n 桥接 - 将现有 workf低low 导出为 n8n 可导入格式"""
import json
from pathlib import Path

workflows_dir = Path("/mnt/d/clawsjoy/workflows")
output_dir = Path("/mnt/d/clawsjoy/data/n8n/import")

output_dir.mkdir(parents=True, exist_ok=True)

for wf_file in workflows_dir.glob("*.json"):
    with open(wf_file) as f:
        wf = json.load(f)
    
    # 转换为 n8n 节点格式（保留你的 skill 调用方式）
    n8n_nodes = []
    for step in wf.get("steps", []):
        node = {
            "name": step.get("name", step.get("skill")),
            "type": "n8n-nodes-base.httpRequest",
            "position": [0, 0],
            "parameters": {
                "url": f"http://localhost:8108/api/promo/make",
                "method": "POST",
                "bodyParameters": step.get("params", {})
            }
        }
        n8n_nodes.append(node)
    
    with open(output_dir / wf_file.name, "w") as f:
        json.dump({"nodes": n8n_nodes}, f, indent=2)

print(f"✅ 已导出 {len(list(workflows_dir.glob('*.json')))} 个工作流到 {output_dir}")
