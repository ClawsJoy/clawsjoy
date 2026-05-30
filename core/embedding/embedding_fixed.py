#!/usr/bin/env python3
"""Embedding Fixed - Embedding Fixed 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from chromadb.utils.embedding_functions import OllamaEmbeddingFunction as _OfficialOllama
from typing import List

EMBEDDING_DIM = 768

class OllamaEmbeddingFunction(_OfficialOllama):
    """官方 OllamaEmbeddingFunction 的包装，保持接口一致"""
    
    def __init__(self, model_name: str = config_helper.get_embedding_model(), url: str = config_helper.get_llm_endpoint()):
        super().__init__(url=url, model_name=model_name)
    
    def embed_query(self, input: str) -> List[float]:
        """查询 embedding - 官方实现已经支持"""
        result = self([input])
        return result[0].tolist() if hasattr(result[0], 'tolist') else list(result[0])
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """文档 embedding"""
        result = self(texts)
        return [r.tolist() if hasattr(r, 'tolist') else list(r) for r in result]

# 测试
if __name__ == "__main__":
    ef = OllamaEmbeddingFunction()
    test_result = ef.embed_query("测试")
    print(f"✅ 官方实现 - 查询维度: {len(test_result)}")
    
    docs_result = ef.embed_documents(["测试1", "测试2"])
    print(f"✅ 官方实现 - 文档维度: {len(docs_result)} 个向量")
