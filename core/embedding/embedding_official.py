#!/usr/bin/env python3
"""Embedding Official - Embedding Official 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import os
from typing import List

from sentence_transformers import SentenceTransformer

# 使用本地模型缓存
MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = "./cache/huggingface"


class LocalEmbeddingFunction:
    """本地 embedding 函数 - 使用 sentence-transformers"""

    def __init__(self):
        print("   加载 embedding 模型...")
        self.model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR)
        print(f"   ✅ 模型已加载: {MODEL_NAME}")

    def __call__(self, input: List[str]) -> List[List[float]]:
        """ChromaDB 要求的接口"""
        return self.model.encode(input, normalize_embeddings=True).tolist()


# 测试
if __name__ == "__main__":
    fn = LocalEmbeddingFunction()
    result = fn(["测试文本"])
    print(f"   维度: {len(result[0])}")
    print("   ✅ 就绪")
