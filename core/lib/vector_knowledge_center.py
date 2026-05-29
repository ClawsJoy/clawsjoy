from typing import List, Dict, Optional
from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config


"""向量知识中心 - 智能知识管理"""

import json
import hashlib
import chromadb
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from chromadb.config import Settings

class VectorKnowledgeCenter:
    """向量知识中心 - 统一管理所有向量化知识"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        # 初始化 ChromaDB 客户端
        self.persist_dir = Path(f"{get_data_root()}/vector_kb")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 知识集合映射
        self.collections = {
            "skills": self.client.get_or_create_collection(
                name="knowledge_skills",
                metadata={"description": "技能知识库"}
            ),
            "agents": self.client.get_or_create_collection(
                name="knowledge_agents",
                metadata={"description": "Agent知识库"}
            ),
            "routes": self.client.get_or_create_collection(
                name="knowledge_routes",
                metadata={"description": "路由知识库"}
            ),
            "memories": self.client.get_or_create_collection(
                name="knowledge_memories",
                metadata={"description": "记忆知识库"}
            ),
            "documents": self.client.get_or_create_collection(
                name="knowledge_documents",
                metadata={"description": "文档知识库"}
            )
        }
        
        print(f"✅ 向量知识中心初始化完成")
        for name, col in self.collections.items():
            print(f"   - {name}: {col.count()} 条")
    
    # ========== 知识入库 ==========
    def add_skill(self, skill_name: str, metadata: Dict) -> str:
        """添加技能知识"""
        doc_id = hashlib.md5(f"skill_{skill_name}".encode()).hexdigest()[:16]
        
        doc = f"""
技能名称: {skill_name}
分类: {metadata.get('category', 'general')}
描述: {metadata.get('description', '')}
关键词: {metadata.get('keywords', skill_name)}
用法: {metadata.get('usage', '')}
        """
        
        self.collections["skills"].upsert(
            ids=[doc_id],
            documents=[doc],
            metadatas=[{
                "type": "skill",
                "name": skill_name,
                "category": metadata.get('category', 'general'),
                "description": metadata.get('description', '')[:200],
                "tags": metadata.get('keywords', skill_name),
                "created_at": datetime.now().isoformat()
            }]
        )
        return doc_id
    
    def add_agent(self, agent_name: str, metadata: Dict) -> str:
        """添加 Agent 知识"""
        doc_id = hashlib.md5(f"agent_{agent_name}".encode()).hexdigest()[:16]
        
        doc = f"""
Agent名称: {agent_name}
类型: {metadata.get('type', 'core')}
能力: {metadata.get('capabilities', '')}
描述: {metadata.get('description', '')}
性格: {metadata.get('personality', 'professional')}
        """
        
        self.collections["agents"].upsert(
            ids=[doc_id],
            documents=[doc],
            metadatas=[{
                "type": "agent",
                "name": agent_name,
                "capabilities": metadata.get('capabilities', ''),
                "personality": metadata.get('personality', 'professional'),
                "created_at": datetime.now().isoformat()
            }]
        )
        return doc_id
    
    def add_memory(self, content: str, user_id: str, category: str = "general") -> str:
        """添加记忆知识"""
        doc_id = hashlib.md5(f"memory_{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        self.collections["memories"].upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[{
                "type": "memory",
                "user_id": user_id,
                "category": category,
                "created_at": datetime.now().isoformat()
            }]
        )
        return doc_id
    
    # ========== 知识检索 ==========
    def search(self, query: str, knowledge_type: str = None, n: int = 10) -> List[Dict]:
        """智能检索"""
        results = []
        
        # 确定搜索范围
        if knowledge_type and knowledge_type in self.collections:
            collections = {knowledge_type: self.collections[knowledge_type]}
        else:
            collections = self.collections
        
        for col_name, collection in collections.items():
            try:
                search_results = collection.query(
                    query_texts=[query],
                    n_results=n
                )
                
                if search_results['documents'] and search_results['documents'][0]:
                    for i, doc in enumerate(search_results['documents'][0]):
                        results.append({
                            "source": col_name,
                            "content": doc[:300],
                            "score": 1 - search_results['distances'][0][i] if search_results['distances'] else 0,
                            "metadata": search_results['metadatas'][0][i] if search_results['metadatas'] else {}
                        })
            except Exception as e:
                print(f"搜索 {col_name} 失败: {e}")
        
        # 按相似度排序
        results.sort(key=lambda x: -x['score'])
        return results[:n]
    
    def search_skills(self, query: str, n: int = 10) -> List[Dict]:
        """搜索技能"""
        return self.search(query, "skills", n)
    
    def search_agents(self, query: str, n: int = 10) -> List[Dict]:
        """搜索 Agent"""
        return self.search(query, "agents", n)
    
    # ========== 知识统计 ==========
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            name: collection.count() 
            for name, collection in self.collections.items()
        }
    
    def get_categories(self) -> Dict:
        """获取分类统计"""
        categories = {}
        for col_name, collection in self.collections.items():
            categories[col_name] = {
                "count": collection.count(),
                "description": collection.metadata.get('description', '')
            }
        return categories
    
    # ========== 知识清理 ==========
    def clear_collection(self, collection_name: str):
        """清空指定集合"""
        if collection_name in self.collections:
            # 获取所有 IDs
            all_data = self.collections[collection_name].get()
            if all_data['ids']:
                self.collections[collection_name].delete(ids=all_data['ids'])
            print(f"✅ 已清空 {collection_name} 集合")
    
    def rebuild_index(self):
        """重建索引"""
        for name in self.collections:
            self.clear_collection(name)
        print("✅ 所有索引已重建")


   # ==================== 会员向量管理 ====================
    
    def add_member(self, user_id: str, metadata: Dict) -> str:
        """添加会员向量 - 用于相似会员推荐和个性化服务"""
        collection = self._get_or_create_collection("butler_members")
        doc_id = f"member_{user_id}"
        
        # 构造会员特征文本（用于向量化）
        content = self._member_to_text(metadata)
        
        # 准备元数据
        meta = {
            "user_id": user_id,
            "butler_name": metadata.get("butler_name", "小管"),
            "level": metadata.get("level", "bronze"),
            "interactions": metadata.get("interactions", 0),
            "achievements": metadata.get("achievements", 0),
            "tags": metadata.get("tags", []),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[meta]
            )
            print(f"✅ 会员向量已添加: {user_id}")
            return doc_id
        except Exception as e:
            print(f"❌ 添加会员向量失败: {e}")
            return ""
    
    def _member_to_text(self, metadata: Dict) -> str:
        """将会员元数据转换为文本特征"""
        parts = [
            f"会员等级: {metadata.get('level', 'bronze')}",
            f"管家名称: {metadata.get('butler_name', '小管')}",
            f"交互次数: {metadata.get('interactions', 0)}",
            f"成就数量: {metadata.get('achievements', 0)}",
        ]
        
        # 添加标签
        tags = metadata.get('tags', [])
        if tags:
            parts.append(f"兴趣标签: {', '.join(tags)}")
        
        return "。".join(parts)
    
    def update_member(self, user_id: str, metadata: Dict) -> bool:
        """更新会员向量"""
        doc_id = f"member_{user_id}"
        collection = self._get_collection("butler_members")
        if not collection:
            return False
        
        content = self._member_to_text(metadata)
        meta = {
            "user_id": user_id,
            "butler_name": metadata.get("butler_name", "小管"),
            "level": metadata.get("level", "bronze"),
            "interactions": metadata.get("interactions", 0),
            "achievements": metadata.get("achievements", 0),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[meta]
            )
            return True
        except Exception:
            # 如果更新失败，尝试添加
            return bool(self.add_member(user_id, metadata))
    
    def search_members(self, query: str, n: int = 10) -> List[Dict]:
        """根据查询文本检索相似会员"""
        collection = self._get_collection("butler_members")
        if not collection:
            return []
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n
            )
            return self._format_member_results(results)
        except Exception as e:
            print(f"❌ 检索会员失败: {e}")
            return []
    
    def search_similar_members(self, user_id: str, n: int = 5) -> List[Dict]:
        """基于现有会员找相似会员（排除自己）"""
        collection = self._get_collection("butler_members")
        if not collection:
            return []
        
        doc_id = f"member_{user_id}"
        
        try:
            # 获取该会员的文档
            result = collection.get(ids=[doc_id])
            if not result['documents']:
                return []
            
            # 用该会员的内容检索相似会员
            results = collection.query(
                query_texts=[result['documents'][0]],
                n_results=n + 1  # 多取一个，排除自己
            )
            
            formatted = self._format_member_results(results)
            # 排除自己
            return [r for r in formatted if r.get('user_id') != user_id][:n]
        except Exception as e:
            print(f"❌ 查找相似会员失败: {e}")
            return []
    
    def _format_member_results(self, results: Dict) -> List[Dict]:
        """格式化会员检索结果"""
        formatted = []
        if not results.get('ids'):
            return formatted
        
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
            formatted.append({
                "user_id": metadata.get("user_id", doc_id.replace("member_", "")),
                "butler_name": metadata.get("butler_name", "小管"),
                "level": metadata.get("level", "bronze"),
                "interactions": metadata.get("interactions", 0),
                "achievements": metadata.get("achievements", 0),
                "similarity_score": results['distances'][0][i] if results.get('distances') else 1.0,
                "content": results['documents'][0][i] if results.get('documents') else ""
            })
        return formatted
    
    def get_member_vector_stats(self) -> Dict:
        """获取会员向量统计"""
        collection = self._get_collection("butler_members")
        if not collection:
            return {"count": 0, "exists": False}
        
        try:
            count = collection.count()
            return {
                "exists": True,
                "count": count,
                "collection_name": "butler_members"
            }
        except Exception as e:
            return {"count": 0, "error": str(e)}


    # ==================== 会员向量管理 ====================
    
    def _get_member_collection(self):
        """获取或创建会员集合"""
        try:
            return self.client.get_collection("butler_members")
        except Exception:
            return self.client.create_collection("butler_members")
    
    def add_member(self, user_id: str, metadata: dict) -> str:
        """添加会员向量"""
        collection = self._get_member_collection()
        doc_id = f"member_{user_id}"
        
        # 构造特征文本
        content = f"等级:{metadata.get('level','bronze')} 管家:{metadata.get('butler_name','小管')} 交互:{metadata.get('interactions',0)} 成就:{metadata.get('achievements',0)}"
        
        collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[{
                "user_id": user_id,
                "butler_name": metadata.get("butler_name", "小管"),
                "level": metadata.get("level", "bronze"),
                "interactions": metadata.get("interactions", 0),
                "achievements": metadata.get("achievements", 0),
                "timestamp": datetime.now().isoformat()
            }]
        )
        return doc_id
    
    def update_member(self, user_id: str, metadata: dict) -> bool:
        """更新会员向量"""
        try:
            collection = self._get_member_collection()
            doc_id = f"member_{user_id}"
            content = f"等级:{metadata.get('level','bronze')} 管家:{metadata.get('butler_name','小管')} 交互:{metadata.get('interactions',0)} 成就:{metadata.get('achievements',0)}"
            collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[{
                    "user_id": user_id,
                    "butler_name": metadata.get("butler_name", "小管"),
                    "level": metadata.get("level", "bronze"),
                    "interactions": metadata.get("interactions", 0),
                    "achievements": metadata.get("achievements", 0),
                    "updated_at": datetime.now().isoformat()
                }]
            )
            return True
        except Exception:
            return False
    
    def search_members(self, query: str, n: int = 10) -> list:
        """搜索相似会员"""
        try:
            collection = self._get_member_collection()
            results = collection.query(query_texts=[query], n_results=n)
            formatted = []
            for i, doc_id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i] if results.get('metadatas') else {}
                formatted.append({
                    "user_id": meta.get("user_id", ""),
                    "butler_name": meta.get("butler_name", ""),
                    "level": meta.get("level", ""),
                    "score": results['distances'][0][i] if results.get('distances') else 1.0
                })
            return formatted
        except Exception:
            return []
    
    def get_member_stats(self) -> dict:
        """获取会员向量统计"""
        try:
            collection = self._get_member_collection()
            return {"count": collection.count(), "exists": True}
        except Exception:
            return {"count": 0, "exists": False}

# 全局实例
vector_knowledge_center = VectorKnowledgeCenter()
