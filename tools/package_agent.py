#!/usr/bin/env python3
"""Agent 商品化打包工具 - 将开发者的 Agent 打包成可上架商品"""

import os
import json
import shutil
import tarfile
import yaml
from pathlib import Path
from datetime import datetime

def sanitize_agent(agent_path: Path):
    """清空用户记忆数据（脱敏）"""
    memory_files = ["memory.json", "preferences.json", "habits.json", "todos.json"]
    for f in memory_files:
        target = agent_path / f
        if target.exists():
            with open(target, 'w') as fp:
                json.dump({"sanitized": True, "data": {}}, fp)
    
    # 清空向量目录
    vector_dir = agent_path / "vectors"
    if vector_dir.exists():
        shutil.rmtree(vector_dir)
        vector_dir.mkdir(parents=True)
    
    print(f"   🧹 已脱敏: {agent_path}")

def package_agent(developer_id: str, agent_name: str, version: str = "1.0.0"):
    """打包 Agent 成商品"""
    dev_agent_path = Path(f"data/users/{developer_id}/agents/{agent_name}")
    
    if not dev_agent_path.exists():
        print(f"❌ Agent 不存在: {dev_agent_path}")
        return
    
    # 1. 脱敏
    sanitize_agent(dev_agent_path)
    
    # 2. 打包
    package_id = f"{developer_id}_{agent_name}_{datetime.now().strftime('%Y%m%d')}"
    package_file = Path(f"data/marketplace/pending/{package_id}.tar.gz")
    
    with tarfile.open(package_file, "w:gz") as tar:
        tar.add(dev_agent_path, arcname=agent_name)
    
    # 3. 创建元数据
    metadata = {
        "package_id": package_id,
        "name": agent_name,
        "version": version,
        "developer": developer_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    with open(Path(f"data/marketplace/pending/{package_id}.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ 打包完成: {package_file}")
    print(f"   等待管理员审核...")
    return package_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("用法: python package_agent.py <developer_id> <agent_name> [version]")
        sys.exit(1)
    
    dev_id = sys.argv[1]
    agent_name = sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else "1.0.0"
    
    package_agent(dev_id, agent_name, version)
