from core.lib.vector_knowledge_center import vector_knowledge_center
#!/usr/bin/env python3
"""Unified Vector Api - Unified Vector Api 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


from pathlib import Path

import chromadb
from flask import Blueprint, jsonify, request

unified_vector_bp = Blueprint("unified_vector", __name__, url_prefix="/api/vector")


@unified_vector_bp.route("/search", methods=["POST"])
def search_all():
    """统一向量检索"""
    data = request.get_json() or {}
    query = data.get("query", "")
    sources = data.get("sources", ["memory", "skills", "knowledge"])
    n = data.get("n", 5)

    if not query:
        return jsonify({"success": False, "error": "query required"}), 400

    results = []

    # 1. 记忆向量
    if "memory" in sources:
        try:
            client = vector_knowledge_center.client
            collection = client.get_collection("memory_vectors")
            res = collection.query(query_texts=[query], n_results=n)
            if res.get("documents") and res["documents"][0]:
                for i, doc in enumerate(res["documents"][0]):
                    results.append(
                        {
                            "source": "memory",
                            "text": doc,
                            "similarity": (
                                1 / (1 + res["distances"][0][i])
                                if res.get("distances")
                                else 0
                            ),
                        }
                    )
        except Exception as e:
            pass

    # 2. 技能向量
    if "skills" in sources:
        try:
            client = vector_knowledge_center.client
            collection = client.get_collection("skill_vectors")
            res = collection.query(query_texts=[query], n_results=n)
            if res.get("documents") and res["documents"][0]:
                for i, doc in enumerate(res["documents"][0]):
                    results.append(
                        {
                            "source": "skills",
                            "text": doc,
                            "similarity": (
                                1 / (1 + res["distances"][0][i])
                                if res.get("distances")
                                else 0
                            ),
                        }
                    )
        except Exception as e:
            pass

    # 3. 知识向量
    if "knowledge" in sources:
        try:
            from lib.knowledge_registry import knowledge_registry

            res = knowledge_registry.search(query, n=n)
            for r in res:
                results.append(
                    {
                        "source": "knowledge",
                        "text": r.get("content", ""),
                        "title": r.get("title", ""),
                        "similarity": r.get("similarity", 0),
                    }
                )
        except Exception as e:
            pass

    results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
    return jsonify({"success": True, "query": query, "results": results[:n]})


@unified_vector_bp.route("/stats", methods=["GET"])
def get_stats():
    """获取向量统计"""
    stats = {}

    # 记忆向量
    try:
        client = vector_knowledge_center.client
        collection = client.get_collection("memory_vectors")
        stats["memory"] = collection.count()
    except Exception as e:
        stats["memory"] = 0

    # 技能向量
    try:
        client = vector_knowledge_center.client
        collection = client.get_collection("skill_vectors")
        stats["skills"] = collection.count()
    except Exception as e:
        stats["skills"] = 0

    # 知识向量 - 从 knowledge_registry 获取真实数量
    try:
        from lib.knowledge_registry import knowledge_registry

        stats["knowledge"] = knowledge_registry.get_stats().get("total_knowledge", 0)
    except Exception as e:
        stats["knowledge"] = 0

    stats["total"] = sum(stats.values())

    return jsonify({"success": True, "stats": stats})


def register_unified_vector_api(app):
    """注册统一向量 API"""
    app.register_blueprint(unified_vector_bp)
    print("   ✅ 统一向量入口 API 已注册")
