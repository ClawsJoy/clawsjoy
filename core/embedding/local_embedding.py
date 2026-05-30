"""本地 Embedding - 使用 Ollama nomic-embed-text"""

import requests
import numpy as np
from typing import List


class LocalEmbedding:
    """本地 embedding 服务 - 使用 Ollama"""
    
    def __init__(self):
        self.url = "http://localhost:11434/api/embeddings"
        self.model = config_helper.get_embedding_model()  # 本地已有模型
    
    def encode(self, text: str) -> List[float]:
        """获取文本的 embedding 向量"""
        try:
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": text},
                timeout=config_helper.get_timeout("default")
            )
            if response.status_code == 200:
                return response.json().get('embedding', [])
        except Exception as e:
            print(f"Embedding 错误: {e}")

        # 降级方案：使用简单哈希
        return self._fallback_embedding(text)
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取 embedding"""
        return [self.encode(t) for t in texts]
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """降级方案：简单哈希向量"""
        import hashlib
        words = text.lower().split()[:30]
        vec = []
        for w in words:
            h = hashlib.md5(w.encode()).hexdigest()[:8]
            vec.append(int(h, 16) % 100 / 100)
        while len(vec) < 30:
            vec.append(0.0)
        return vec


embedding_model = LocalEmbedding()
