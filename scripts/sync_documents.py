#!/usr/bin/env python3
"""文档同步脚本 - 同步文档到向量索引"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def sync_documents():
    """同步文档到向量索引"""
    print("🔄 开始同步文档...")

    try:
        from core.lib.vector_knowledge_center import vector_knowledge_center
        from engine.document.core import document_engine

        docs = document_engine.documents
        synced = 0

        for doc_id, doc in docs.items():
            try:
                vector_knowledge_center.add_document(
                    doc_id=f"doc_{doc_id}",
                    content=f"{doc['name']} {doc.get('type', '')}",
                    metadata=doc,
                    collection="documents",
                )
                synced += 1
            except Exception as e:
                pass

        print(f"   ✅ 已同步 {synced}/{len(docs)} 个文档")
        return synced
    except Exception as e:
        print(f"   ❌ 同步失败: {e}")
        return 0


if __name__ == "__main__":
    sync_documents()
