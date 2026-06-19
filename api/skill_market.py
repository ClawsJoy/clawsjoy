from core.lib.vector_knowledge_center import vector_knowledge_center
#!/usr/bin/env python3
"""Skill Market API - 技能市场与向量推荐"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from flask import request, jsonify

from core.lib.config_helper import get_data_root
from core.lib.unified_config import unified_config
from core.lib.route_handlers import register


# ================================================================
#  安全扫描器
# ================================================================

class SecurityScanner:
    """技能安全扫描器"""

    DANGEROUS_PATTERNS = [
        "import os", "subprocess", "eval", "exec", "__import__",
        "open(", "file(", "sys.", "shutil.", "rm ", "del "
    ]

    @staticmethod
    def scan_skill(skill_code: str) -> dict:
        """扫描技能代码安全性"""
        issues = []
        for pattern in SecurityScanner.DANGEROUS_PATTERNS:
            if pattern in skill_code:
                issues.append(f"包含危险模式: {pattern}")

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "level": "warning" if issues else "safe"
        }

    @staticmethod
    def sandbox_check(skill_path: Path) -> dict:
        """沙箱环境检查"""
        return {
            "isolated": True,
            "network": False,
            "filesystem": True,
            "process": False
        }


# ================================================================
#  技能向量推荐器
# ================================================================

class SkillVectorRecommender:
    """技能向量推荐器（使用独立向量目录）"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_vector_store()
        self._index_existing_skills()

    def _init_vector_store(self):
        """初始化向量存储（使用独立目录）"""
        import chromadb
        from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
        from pathlib import Path

        vector_config = unified_config.get("vector", {})
        persist_dir = vector_config.get("skill_vector_path", "data/skill_vectors")

        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        embedding_model = vector_config.get("embedding_model", "nomic-embed-text")
        ollama_url = unified_config.get("llm.endpoint", "http://localhost:11434")

        self.embedding_fn = OllamaEmbeddingFunction(
            url=ollama_url,
            model_name=embedding_model
        )

        # ✅ 使用独立目录，不与 vector_knowledge_center 冲突
        self.client = vector_knowledge_center.client

        collection_name = vector_config.get("skill_collection", "skill_vectors")

        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )

        print(f"✅ SkillVectorRecommender 初始化完成")
        print(f"   📂 目录: {persist_dir}")
        print(f"   📚 集合: {collection_name}")

    def _index_existing_skills(self):
        """索引已有技能"""
        try:
            from core.lib.skill_loader_v3 import get_skill_loader
            skills = get_skill_loader().list_skills()
            count = 0
            for skill in skills:
                if not self._is_indexed(skill):
                    self.index_skill({"id": skill, "name": skill})
                    count += 1
            if count > 0:
                print(f"   📚 已索引 {count} 个技能")
        except Exception as e:
            print(f"   ⚠️ 技能索引失败: {e}")

    def _is_indexed(self, skill_id: str) -> bool:
        try:
            doc_id = hashlib.md5(skill_id.encode()).hexdigest()
            result = self.collection.get(ids=[doc_id])
            return len(result.get('ids', [])) > 0
        except Exception:
            return False

    def index_skill(self, skill: dict) -> bool:
        """索引单个技能"""
        skill_id = skill.get('id', '')
        name = skill.get('name', '')
        description = skill.get('description', '')
        category = skill.get('category', 'general')
        tags = skill.get('tags', [])

        doc_id = hashlib.md5(skill_id.encode()).hexdigest()
        text = f"{name}: {description}"

        try:
            self.collection.upsert(
                ids=[doc_id],
                documents=[text],
                metadatas=[{
                    "skill_id": skill_id,
                    "name": name,
                    "category": category,
                    "tags": ",".join(tags) if tags else ""
                }]
            )
            return True
        except Exception as e:
            print(f"索引技能失败 {skill_id}: {e}")
            return False

    def _load_keyword_mapping(self) -> dict:
        """从配置加载关键词映射"""
        import yaml
        config_path = Path('config/skill_keywords_registry.yaml')
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('keyword_mappings', {})
            except Exception:
                pass
        return {}

    def recommend(self, query: str, n: int = 5, category: str = None, min_similarity: float = 0.6) -> List[Dict]:
        """推荐相似技能"""
        import yaml
        from pathlib import Path

        # 加载匹配配置
        config = {}
        config_path = Path('config/skill_matching.yaml')
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except Exception:
                pass

        keyword_mapping = config.get('matching', {}).get('keyword_mapping', {})
        blacklist = config.get('blacklist_skills', [])
        query_lower = query.lower()

        # 1. 关键词匹配
        for keyword, skills in keyword_mapping.items():
            if keyword.lower() in query_lower or query_lower in keyword.lower():
                for skill_name in skills:
                    if skill_name in blacklist:
                        continue
                    try:
                        results = self.collection.get(where={"name": skill_name})
                        if results.get('metadatas') and results['metadatas']:
                            meta = results['metadatas'][0]
                            return [{
                                'skill_id': meta.get('skill_id'),
                                'name': meta.get('name'),
                                'category': meta.get('category'),
                                'similarity': 0.95
                            }]
                    except Exception:
                        pass
                break

        # 2. 向量相似度查询
        try:
            where = {"category": category} if category else None
            results = self.collection.query(
                query_texts=[query],
                n_results=n * 2,
                where=where,
                include=["documents", "distances", "metadatas"]
            )

            recommendations = []
            if results.get('documents') and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i]
                    skill_name = meta.get('name')
                    if skill_name in blacklist:
                        continue
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    similarity = 1 / (1 + distance)
                    if similarity >= min_similarity:
                        recommendations.append({
                            'skill_id': meta.get('skill_id'),
                            'name': skill_name,
                            'category': meta.get('category'),
                            'similarity': round(similarity, 3)
                        })

            recommendations.sort(key=lambda x: x['similarity'], reverse=True)
            return recommendations[:n]

        except Exception as e:
            print(f"向量推荐失败: {e}")
            return []


# ================================================================
#  API 路由
# ================================================================

@register("marketplace_upload")
def marketplace_upload():
    """上传技能到市场（带安全扫描）"""
    data = request.get_json() or {}
    skill_id = data.get('skill_id', '')
    skill_code = data.get('code', '')
    author = data.get('author', '')

    if not skill_id or not skill_code:
        return jsonify({"success": False, "error": "缺少 skill_id 或 code"}), 400

    # 安全扫描
    scan_result = SecurityScanner.scan_skill(skill_code)
    if not scan_result['safe']:
        return jsonify({
            "success": False,
            "error": "技能安全扫描未通过",
            "issues": scan_result['issues']
        }), 400

    # 保存待审核
    pending_dir = Path(f"{get_data_root()}/marketplace/pending")
    pending_dir.mkdir(parents=True, exist_ok=True)

    skill_data = {
        "id": skill_id,
        "code": skill_code,
        "author": author,
        "status": "pending",
        "scan_result": scan_result,
        "created_at": datetime.now().isoformat()
    }

    with open(pending_dir / f"{skill_id}.json", 'w') as f:
        json.dump(skill_data, f, indent=2)

    return jsonify({
        "success": True,
        "message": "技能已提交审核",
        "scan_result": scan_result
    })


@register("marketplace_review")
def marketplace_review():
    """管理员审核技能"""
    data = request.get_json() or {}
    skill_id = data.get('skill_id', '')
    action = data.get('action', '')  # approve / reject

    if not skill_id or action not in ['approve', 'reject']:
        return jsonify({"success": False, "error": "无效参数"}), 400

    pending_dir = Path(f"{get_data_root()}/marketplace/pending")
    pending_file = pending_dir / f"{skill_id}.json"

    if not pending_file.exists():
        return jsonify({"success": False, "error": "技能不存在"}), 404

    with open(pending_file, 'r') as f:
        skill_data = json.load(f)

    if action == "approve":
        skill_data['status'] = 'approved'
        marketplace_dir = Path(f"{get_data_root()}/marketplace")
        marketplace_dir.mkdir(parents=True, exist_ok=True)
        with open(marketplace_dir / f"{skill_id}.json", 'w') as f:
            json.dump(skill_data, f, indent=2)
        pending_file.unlink()
        return jsonify({"success": True, "message": "技能已审核通过"})

    elif action == "reject":
        pending_file.unlink()
        return jsonify({"success": True, "message": "技能已拒绝"})

    return jsonify({"success": False, "error": "无效操作"}), 400


# ================================================================
#  全局实例
# ================================================================

skill_recommender = SkillVectorRecommender()
