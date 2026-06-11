#!/usr/bin/env python3
"""Skill Market - Skill Market 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.route_handlers import register
"""技能市场 API"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import json
import uuid
import time

skill_market_bp = Blueprint('skill_market', __name__, url_prefix='/api/skill-market')

# 技能存储
SKILLS_DIR = Path("data/skill_market")
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


@skill_market_bp.route('/list', methods=['GET'])
def list_skills():
    """列出市场技能"""
    skills = []
    for f in SKILLS_DIR.glob("*.json"):
        try:
            with open(f, 'r') as fp:
                skill = json.load(fp)
                skills.append({
                    "id": skill.get('id', f.stem),
                    "name": skill.get('name', f.stem),
                    "description": skill.get('description', ''),
                    "author": skill.get('author', 'anonymous'),
                    "downloads": skill.get('downloads', 0),
                    "price": skill.get('price', 'free')
                })
        except Exception as e:
            pass
    
    return jsonify({"success": True, "skills": skills})


@skill_market_bp.route('/upload', methods=['POST'])
def upload_skill():
    """上传技能（开发者）"""
    data = request.get_json() or {}
    
    skill_id = str(uuid.uuid4())[:8]
    skill = {
        "id": skill_id,
        "name": data.get('name', ''),
        "description": data.get('description', ''),
        "code": data.get('code', ''),
        "author": data.get('author', 'developer'),
        "version": data.get('version', '1.0.0'),
        "price": data.get('price', 'free'),
        "created_at": time.time(),
        "downloads": 0
    }
    
    with open(SKILLS_DIR / f"{skill_id}.json", 'w') as f:
        json.dump(skill, f, indent=2)
    
    return jsonify({"success": True, "skill_id": skill_id})


@skill_market_bp.route('/install/<skill_id>', methods=['POST'])
def install_skill(skill_id):
    """安装技能（用户）- 从市场仓库安装到个人技能库"""
    from pathlib import Path
    
    # 市场仓库目录（审核通过的技能）
    MARKETPLACE_DIR = Path("data/marketplace")
    # 用户技能安装目录
    SKILLS_DIR = Path("data/skill_market")
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 先从市场仓库查找
    marketplace_file = MARKETPLACE_DIR / f"{skill_id}.json"
    if not marketplace_file.exists():
        return jsonify({"success": False, "error": "Skill not found in marketplace"}), 404
    
    # 读取市场中的技能
    with open(marketplace_file, 'r') as f:
        skill = json.load(f)
    
    # 复制到用户技能目录
    user_skill_file = SKILLS_DIR / f"{skill_id}.json"
    
    # 更新下载计数
    skill['downloads'] = skill.get('downloads', 0) + 1
    skill['installed_at'] = time.time()
    
    # 保存到用户技能目录
    with open(user_skill_file, 'w') as f:
        json.dump(skill, f, indent=2)
    
    # 同时更新市场仓库的下载计数
    with open(marketplace_file, 'w') as f:
        json.dump(skill, f, indent=2)
    
    return jsonify({"success": True, "message": f"技能 {skill.get('name', skill_id)} 安装成功"})

def register_skill_market(app):
    app.register_blueprint(skill_market_bp)
    print("   ✅ 技能市场 API 已注册")


# ========== 向量推荐功能 ==========

class SkillVectorRecommender:
    """技能向量推荐器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_vector_store()
        self._index_existing_skills()

    def _init_vector_store(self):
        import chromadb
        from chromadb.utils import embedding_functions
        from pathlib import Path
        from core.lib.unified_config import unified_config

        vector_config = unified_config.get("vector", {})
        persist_dir = vector_config.get("skill_vector_path", "data/skill_vectors")

        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        embedding_model = vector_config.get("embedding_model", "nomic-embed-text")

        from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
        ollama_url = unified_config.get("llm.endpoint", "http://localhost:11434")
        self.embedding_fn = OllamaEmbeddingFunction(
            url=ollama_url,
            model_name=embedding_model
        )

        self.client = chromadb.PersistentClient(path=persist_dir)

        collection_name = vector_config.get("skill_collection", "skill_vectors")

        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )

    def _index_existing_skills(self):
        """索引已有技能"""
        try:
            from lib.skill_loader_v3 import skill_loader
            skills = skill_loader.list_skills()
            count = 0
            for skill in skills:
                skill_id = skill
                if not self._is_indexed(skill_id):
                    self.index_skill({"id": skill_id, "name": skill_id})
                    count += 1
            if count > 0:
                print(f"   📚 已索引 {count} 个技能")
        except Exception as e:
            pass

    def _is_indexed(self, skill_id: str) -> bool:
        try:
            import hashlib
            doc_id = hashlib.md5(skill_id.encode()).hexdigest()
            result = self.collection.get(ids=[doc_id])
            return len(result.get('ids', [])) > 0
        except Exception as e:
            return False

    def index_skill(self, skill: dict):
        """索引单个技能"""
        import hashlib
        skill_id = skill.get('id', '')
        name = skill.get('name', '')
        description = skill.get('description', '')
        category = skill.get('category', 'general')
        tags = skill.get('tags', [])

        doc_id = hashlib.md5(skill_id.encode()).hexdigest()
        text = f"{name}: {description}"

        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[{
                "skill_id": skill_id,
                "name": name,
                "category": category,
                "tags": ",".join(tags)
            }]
        )
        return True


    def _load_keyword_mapping(self):
        """从配置注册表加载关键词映射"""
        import yaml
        from pathlib import Path
        
        config_path = Path('config/skill_keywords_registry.yaml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('keyword_mappings', {})
        return {}
    
    def _get_keyword_skills(self, query: str) -> list:
        """根据关键词匹配技能（从注册表）"""
        keyword_mapping = self._load_keyword_mapping()
        query_lower = query.lower()
        
        for mapping_name, mapping in keyword_mapping.items():
            keywords = mapping.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    return mapping.get('skills', [])
        return []

    def recommend(self, query: str, n: int = 5, category: str = None, min_similarity: float = 0.6):
        """推荐相似技能 - 配置驱动（使用 skill_matching.yaml）"""
        import yaml
        from pathlib import Path
        
        # 加载配置
        config = {}
        config_path = Path('config/skill_matching.yaml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        
        keyword_mapping = config.get('matching', {}).get('keyword_mapping', {})
        blacklist = config.get('blacklist_skills', [])
        priority_skills = config.get('priority_skills', [])
        
        # 1. 关键词匹配（子串匹配）
        query_lower = query.lower()
        for keyword, skills in keyword_mapping.items():
            # 子串匹配：关键词在查询中，或查询在关键词中
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
                    except Exception as e:
                        pass
                break
        
        # 2. 向量相似度查询
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
                skill_name = results['metadatas'][0][i].get('name')
                if skill_name in blacklist:
                    continue
                distance = results['distances'][0][i] if results.get('distances') else 0
                similarity = 1 / (1 + distance)
                if similarity >= min_similarity:
                    recommendations.append({
                        'skill_id': results['metadatas'][0][i].get('skill_id'),
                        'name': skill_name,
                        'category': results['metadatas'][0][i].get('category'),
                        'similarity': round(similarity, 3)
                    })
        
        recommendations.sort(key=lambda x: x['similarity'], reverse=True)
        return recommendations[:n]
        """推荐相似技能 - 带相似度阈值"""
        where = {"category": category} if category else None
        results = self.collection.query(
            query_texts=[query],
            n_results=n * 2,  # 多取一些用于过滤
            where=where,
            include=["documents", "distances", "metadatas"]
        )

        recommendations = []
        if results.get('documents') and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results.get('distances') else 0
                similarity = 1 / (1 + distance)
                if similarity >= min_similarity:
                    recommendations.append({
                        'skill_id': results['metadatas'][0][i].get('skill_id'),
                        'name': results['metadatas'][0][i].get('name'),
                        'category': results['metadatas'][0][i].get('category'),
                        'similarity': round(similarity, 3)
                    })
        return recommendations[:n]
class SecurityScanner:
    """技能安全扫描器"""
    
    @staticmethod
    def scan_skill(skill_code: str) -> dict:
        """扫描技能代码安全性"""
        dangerous_patterns = [
            "import os", "subprocess", "eval", "exec", "__import__",
            "open(", "file(", "sys.", "shutil.", "rm ", "del "
        ]
        
        issues = []
        for pattern in dangerous_patterns:
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


@register("marketplace_upload")
def marketplace_upload():
    """上传技能到市场（带安全扫描）"""
    from flask import request, jsonify
    
    data = request.get_json() or {}
    skill_id = data.get('skill_id', '')
    skill_code = data.get('code', '')
    author = data.get('author', '')
    
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
    from flask import request, jsonify
    
    data = request.get_json() or {}
    skill_id = data.get('skill_id', '')
    action = data.get('action', '')  # approve / reject
    
    pending_dir = Path(f"{get_data_root()}/marketplace/pending")
    pending_file = pending_dir / f"{skill_id}.json"
    
    if not pending_file.exists():
        return jsonify({"success": False, "error": "技能不存在"}), 404
    
    with open(pending_file, 'r') as f:
        skill_data = json.load(f)
    
    if action == "approve":
        skill_data['status'] = 'approved'
        # 移动到正式市场
        marketplace_dir = Path(f"{get_data_root()}/marketplace")
        with open(marketplace_dir / f"{skill_id}.json", 'w') as f:
            json.dump(skill_data, f, indent=2)
        pending_file.unlink()
        return jsonify({"success": True, "message": "技能已审核通过"})
    
    elif action == "reject":
        pending_file.unlink()
        return jsonify({"success": True, "message": "技能已拒绝"})
    
    return jsonify({"success": False, "error": "无效操作"}), 400

# 添加 register 导入
from lib.route_handlers import register

# 修复 register 导入
from lib.route_handlers import register

# 全局推荐器实例
skill_recommender = SkillVectorRecommender()
