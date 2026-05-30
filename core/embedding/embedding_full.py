#!/usr/bin/env python3
"""Embedding Full - Embedding Full 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import requests
from typing import List


class OllamaEmbeddingFunction:
    """完全兼容 ChromaDB 的 Embedding 函数"""
    
    def __init__(self, model_name: str = config_helper.get_embedding_model(), url: str = "http://localhost:11434/api/embeddings"):
        self.model_name = model_name
        self.url = url
    
    def name(self) -> str:
        """ChromaDB 需要的 name 方法"""
        return f"ollama_{self.model_name}"
    
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
        return [self._get_embedding(t) for t in texts]
    
    def embed_query(self, query: str) -> List[float]:
        """ChromaDB 需要的 embed_query 方法"""
        return self._get_embedding(query)
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """兼容旧版调用方式"""
        return self.embed_documents(input)


# 测试
if __name__ == "__main__":
    print("测试完全兼容的 Embedding 函数...")
    fn = OllamaEmbeddingFunction()
    
    print(f"   name: {fn.name()}")
    print(f"   embed_query 维度: {len(fn.embed_query('测试'))}")
    print(f"   embed_documents 数量: {len(fn.embed_documents(['a', 'b']))}")
    
    print("   ✅ 就绪")
