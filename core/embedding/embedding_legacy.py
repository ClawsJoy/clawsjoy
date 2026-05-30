#!/usr/bin/env python3
"""Embedding Legacy - Embedding Legacy 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import requests
from typing import List


class OllamaEmbeddingLegacy:
    """兼容旧版 ChromaDB 的 Embedding 函数"""
    
    def __init__(self, model_name: str = config_helper.get_embedding_model(), url: str = "http://localhost:11434/api/embeddings"):
        self.model_name = model_name
        self.url = url
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """旧版接口：参数名是 'texts'"""
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    self.url,
                    json={"model": self.model_name, "prompt": text},
                    timeout=config_helper.get_timeout("default")
                )
                if response.status_code == 200:
                    embedding = response.json().get('embedding', [])
                    embeddings.append(embedding)
                else:
                    embeddings.append([0.0] * 768)
            except Exception as e:
                print(f"   ❌ Embedding 错误: {e}")
                embeddings.append([0.0] * 768)

        return embeddings


if __name__ == "__main__":
    print("测试 embedding...")
    fn = OllamaEmbeddingLegacy()
    result = fn(["测试"])
    print(f"   维度: {len(result[0])}")
    print("   ✅ 就绪")
