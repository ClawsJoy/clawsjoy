#!/usr/bin/env python3
"""
ClawsJoy 向量记忆检索系统
"""

import sys
import re
import json
import pickle
import requests
from pathlib import Path
from datetime import datetime

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False
    print("⚠️ 请安装: pip install numpy scikit-learn")

CLAWSJOY_ROOT = Path("/root/clawsjoy")
TENANTS_ROOT = CLAWSJOY_ROOT / "tenants"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://redis:11434"


def get_embedding(text):
    """获取文本向量"""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text[:800]},
            timeout=30,
        )
        return resp.json().get("embedding", []) if resp.status_code == 200 else []
    except:
        return []


class VectorMemory:
    def __init__(self, tenant_id, agent="main"):
        self.memory_path = (
            TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / agent / "evolution"
        )
        self.index_path = self.memory_path / ".vectors.pkl"
        self.chunks = []
        self.embeddings = []

    def load_or_build(self):
        if self.index_path.exists():
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
                self.chunks = data["chunks"]
                self.embeddings = data["embeddings"]
            return True
        return self._build()

    def _build(self):
        learnings_file = self.memory_path / "LEARNINGS.md"
        if not learnings_file.exists():
            return False
        content = learnings_file.read_text(encoding="utf-8")
        # 分块
        self.chunks = [
            c.strip() for c in re.split(r"\n##\s+", content) if len(c.strip()) > 50
        ]
        for chunk in self.chunks:
            emb = get_embedding(chunk[:500])
            if emb:
                self.embeddings.append(emb)
        if self.embeddings:
            with open(self.index_path, "wb") as f:
                pickle.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f)
        return len(self.embeddings) > 0

    def search(self, query, top_k=3):
        if not HAS_VECTOR or not self.load_or_build() or not self.embeddings:
            return []
        q_emb = get_embedding(query)
        if not q_emb:
            return []
        q_vec = np.array(q_emb).reshape(1, -1)
        emb_mat = np.array(self.embeddings)
        scores = cosine_similarity(q_vec, emb_mat)[0]
        idxs = np.argsort(scores)[-top_k:][::-1]
        return [
            {"score": float(scores[i]), "content": self.chunks[i][:400]}
            for i in idxs
            if scores[i] > 0.3
        ]


def retrieve_vector(tenant_id, query):
    vm = VectorMemory(tenant_id)
    results = vm.search(query)
    if not results:
        return ""
    out = f"\n## 🔍 向量检索结果\n\n"
    for i, r in enumerate(results, 1):
        out += f"### {i}. 相似度: {r['score']:.3f}\n{r['content']}\n\n"
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "retrieve":
        print(retrieve_vector(int(sys.argv[2]), " ".join(sys.argv[3:])))
    else:
        print("用法: memory_retriever_v2.py retrieve <tenant_id> <query>")
