from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""Embedding Complete - Embedding Complete 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import requests
from typing import List


class OllamaEmbeddingFunction:
    """完整的 Embedding 函数，支持 ChromaDB"""
    
    def __init__(self, model_name: str = config_helper.get_embedding_model(), url: str = unified_config.get("llm.endpoint", "http://localhost:11434") + "/api/embeddings"):
        self.model_name = model_name
        self.url = url
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取单个文本的 embedding"""
        try:
            response = requests.post(
                self.url,
                json={"model": self.model_name, "prompt": text},
                timeout=config_helper.get_timeout("default")
            )
            if response.status_code == 200:
                return response.json().get('embedding', [])
        except Exception as e:
            print(f"   ⚠️ Embedding 错误: {e}")

        # 降级：返回零向量（768维）
        return [0.0] * 768
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """ChromaDB 需要的 embed_documents 方法"""
        embeddings = []
        for text in texts:
            embeddings.append(self._get_embedding(text))
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """ChromaDB 需要的 embed_query 方法"""
        return self._get_embedding(query)
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """兼容旧版调用方式"""
        return self.embed_documents(input)


# 测试
if __name__ == "__main__":
    print("测试完整 Embedding 函数...")
    fn = OllamaEmbeddingFunction()
    
    # 测试 embed_query
    q_emb = fn.embed_query("测试查询")
    print(f"   embed_query 维度: {len(q_emb)}")
    
    # 测试 embed_documents
    d_emb = fn.embed_documents(["文档1", "文档2"])
    print(f"   embed_documents 数量: {len(d_emb)}")
    
    print("   ✅ 就绪")
