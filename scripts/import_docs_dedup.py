#!/usr/bin/env python3
"""去重导入文档到向量库"""

import hashlib
import json
from pathlib import Path
from lib.memory_vector import vector_memory

def get_doc_hash(content):
    """计算文档哈希"""
    return hashlib.md5(content.encode()).hexdigest()

def import_dedup(file_path, category, metadata=None):
    """去重导入"""
    p = Path(file_path)
    if not p.exists():
        print(f"  ⚠️ 不存在: {p.name}")
        return False
    
    content = p.read_text(encoding='utf-8')
    doc_hash = get_doc_hash(content)
    
    # 检查是否已存在
    hash_file = Path("data/imported_hashes.json")
    imported = {}
    if hash_file.exists():
        try:
            with open(hash_file, 'r') as f:
                imported = json.load(f)
        except:
            imported = {}
    
    if doc_hash in imported:
        print(f"  ⏭️ 跳过（已存在）: {p.name}")
        return False
    
    # 导入
    vector_memory.add(
        content,
        category=category,
        metadata=metadata or {"source": p.name, "version": "4.0.0"}
    )
    
    # 记录哈希
    imported[doc_hash] = {"file": p.name, "category": category}
    with open(hash_file, 'w') as f:
        json.dump(imported, f, indent=2)
    
    print(f"  ✅ 已导入: {p.name}")
    return True

if __name__ == "__main__":
    print("去重导入文档到向量库")
    print("=" * 40)
    
    docs = [
        ("docs/reports/PHASE_4_REPORT.md", "report"),
        ("docs/user_guide_v4.md", "user_guide"),
        ("docs/admin_guide_v4.md", "admin_guide"),
        ("docs/architect_guide_v4.md", "architect_guide"),
        ("docs/agent_handbook_v4.md", "agent_handbook"),
    ]
    
    for doc_path, category in docs:
        import_dedup(doc_path, category)
    
    stats = vector_memory.get_stats()
    print(f"\n📊 向量库统计: {stats}")
