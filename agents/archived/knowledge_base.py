"""知识库索引 - 基于 Qdrant 向量搜索"""

import requests
import hashlib

class KnowledgeBase:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.qdrant_url = "http://localhost:6333"
        self.collection_name = f"kb_{tenant_id}"
        self._init_collection()
    
    def _init_collection(self):
        """初始化集合"""
        try:
            requests.put(f"{self.qdrant_url}/collections/{self.collection_name}", json={
                "vectors": {"size": 384, "distance": "Cosine"}
            })
        except:
            pass
    
    def _simple_vector(self, text):
        """简单向量（生产环境可用 embedding 模型）"""
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        return [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, 16, 2)] + [0.0] * (384 - 8)
    
    def add_document(self, doc_id, text, metadata=None):
        """添加文档到知识库"""
        vector = self._simple_vector(text)
        point = {
            "id": abs(hash(doc_id)) % 10**9,
            "vector": vector,
            "payload": {"text": text, "metadata": metadata or {}, "doc_id": doc_id}
        }
        requests.put(f"{self.qdrant_url}/collections/{self.collection_name}/points", 
                    json={"points": [point]})
    
    def search(self, query, limit=3):
        """搜索相关文档"""
        vector = self._simple_vector(query)
        resp = requests.post(f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                            json={"vector": vector, "limit": limit, "with_payload": True})
        if resp.status_code == 200:
            return [p["payload"]["text"] for p in resp.json().get("result", [])]
        return []
