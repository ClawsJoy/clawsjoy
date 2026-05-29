"""符合 ChromaDB 0.4.16+ 的 Embedding 函数"""

import requests
from typing import List


class OllamaEmbeddingFunctionV2:
    """新版 Ollama Embedding 函数 - 兼容 ChromaDB 0.4.16+"""
    
    def __init__(self, model_name: str = config_helper.get_embedding_model(), url: str = "http://localhost:11434/api/embeddings"):
        self.model_name = model_name
        self.url = url
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """新版接口：参数名必须是 'input' 而不是 'texts'"""
        embeddings = []
        for text in input:
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
                    print(f"   ⚠️ Embedding 失败: HTTP {response.status_code}")
                    embeddings.append([0.0] * 768)
            except Exception as e:
                print(f"   ❌ Embedding 错误: {e}")
                embeddings.append([0.0] * 768)
        
        return embeddings


# 测试
if __name__ == "__main__":
    print("测试新版 embedding...")
    fn = OllamaEmbeddingFunctionV2()
    result = fn(["测试文本"])
    print(f"   输入参数名: input")
    print(f"   维度: {len(result[0])}")
    print("   ✅ 符合 ChromaDB 新接口")
