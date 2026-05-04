#!/usr/bin/env python3
"""
ClawsJoy 完整版记忆检索系统
- 关键词检索（快速）
- 向量检索（精准）
- 自动 Skill 生成
"""

import sys
import re
import json
import pickle
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# 尝试导入向量库
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False
    print("⚠️ 向量检索未启用，请安装: pip install numpy scikit-learn")

# 配置
OLLAMA_URL = "http://redis:11434"
EMBEDDING_MODEL = "nomic-embed-text"  # 需要先拉取: ollama pull nomic-embed-text
CLAWSJOY_ROOT = Path("/root/clawsjoy")
TENANTS_ROOT = CLAWSJOY_ROOT / "tenants"
SKILLS_ROOT = CLAWSJOY_ROOT / "skills"


def get_embedding(text: str) -> Optional[List[float]]:
    """调用 Ollama 获取文本向量"""
    if not HAS_VECTOR:
        return None
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text[:800]},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", [])
    except Exception as e:
        print(f"⚠️ Embedding 失败: {e}")
    return None


class KeywordRetriever:
    """关键词检索器"""
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        words += re.findall(r'[a-zA-Z]{3,}', text.lower())
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去'}
        return [w for w in words if w not in stopwords]
    
    @staticmethod
    def search(memory_text: str, query: str, top_k: int = 3) -> List[Dict]:
        query_kws = KeywordRetriever.extract_keywords(query)
        if not query_kws:
            return []
        
        sections = re.split(r'\n##\s+', memory_text)
        results = []
        for sec in sections:
            if not sec.strip():
                continue
            score = sum(1 for kw in query_kws if kw in sec.lower())
            if score > 0:
                title = sec.split('\n')[0].strip()
                results.append({
                    "title": title,
                    "content": sec.strip()[:500],
                    "score": score,
                    "type": "keyword"
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


class VectorRetriever:
    """向量检索器"""
    
    def __init__(self, tenant_id: int, agent: str = "main"):
        self.memory_path = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / agent / "evolution"
        self.index_path = self.memory_path / ".vectors.pkl"
        self.chunks = []
        self.embeddings = []
    
    def _chunk_memory(self, content: str) -> List[str]:
        chunks = []
        for sec in re.split(r'\n##\s+', content):
            if len(sec.strip()) > 50:
                chunks.append(sec.strip()[:800])
        return chunks
    
    def build_index(self):
        learnings_file = self.memory_path / "LEARNINGS.md"
        if not learnings_file.exists():
            return False
        content = learnings_file.read_text(encoding='utf-8')
        self.chunks = self._chunk_memory(content)
        for chunk in self.chunks:
            emb = get_embedding(chunk)
            if emb:
                self.embeddings.append(emb)
        if self.embeddings:
            with open(self.index_path, 'wb') as f:
                pickle.dump({'chunks': self.chunks, 'embeddings': self.embeddings}, f)
        return len(self.embeddings) > 0
    
    def load_index(self) -> bool:
        if self.index_path.exists():
            with open(self.index_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.embeddings = data['embeddings']
            return True
        return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not HAS_VECTOR or not self.load_index() and not self.build_index():
            return []
        if not self.embeddings:
            return []
        q_emb = get_embedding(query)
        if not q_emb:
            return []
        q_vec = np.array(q_emb).reshape(1, -1)
        emb_mat = np.array(self.embeddings)
        scores = cosine_similarity(q_vec, emb_mat)[0]
        idxs = np.argsort(scores)[-top_k:][::-1]
        results = []
        for i in idxs:
            if scores[i] > 0.3:
                results.append({
                    "content": self.chunks[i][:400],
                    "score": float(scores[i]),
                    "type": "vector"
                })
        return results


class MemoryManager:
    """统一记忆管理器"""
    
    def __init__(self, tenant_id: int, agent: str = "main"):
        self.tenant_id = tenant_id
        self.keyword = KeywordRetriever()
        self.vector = VectorRetriever(tenant_id, agent)
        self.memory_path = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / agent / "evolution"
    
    def load_memories(self) -> str:
        p = self.memory_path / "LEARNINGS.md"
        return p.read_text(encoding='utf-8') if p.exists() else ""
    
    def retrieve(self, query: str, use_vector: bool = True, top_k: int = 3) -> Tuple[List[Dict], str]:
        memory_text = self.load_memories()
        if not memory_text:
            return [], "无记忆"
        
        # 先尝试关键词
        kw_results = self.keyword.search(memory_text, query, top_k)
        if kw_results and kw_results[0].get("score", 0) >= 2:
            return kw_results, "关键词匹配"
        
        # 再尝试向量
        if use_vector and HAS_VECTOR:
            vec_results = self.vector.search(query, top_k)
            if vec_results:
                return vec_results, "向量匹配"
        
        return kw_results, "关键词匹配（低质量）"
    
    def format_context(self, results: List[Dict], method: str) -> str:
        if not results:
            return ""
        out = f"\n## 📚 相关历史经验（{method}）\n\n"
        for i, r in enumerate(results, 1):
            if r.get("type") == "vector":
                out += f"### {i}. 相似记忆（相似度: {r['score']:.3f}）\n"
            else:
                out += f"### {i}. {r.get('title', '记忆')}\n"
            out += f"{r['content']}\n\n"
        return out


class SkillGenerator:
    """自动 Skill 生成器"""
    
    def __init__(self, tenant_id: int, agent: str = "main"):
        self.success_path = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / agent / "evolution" / "SUCCESSES.md"
        self.skills_dir = SKILLS_ROOT / "auto_generated"
    
    def generate(self) -> List[str]:
        if not self.success_path.exists():
            return []
        content = self.success_path.read_text(encoding='utf-8')
        cases = re.split(r'\n##\s+', content)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        for case in cases:
            if not case.strip():
                continue
            title = case.split('\n')[0].strip()
            skill_name = re.sub(r'[^\w\-]', '', title.replace(' ', '_').lower())[:50]
            skill_path = self.skills_dir / f"{skill_name}.md"
            if skill_path.exists():
                continue
            skill_content = f"""---
name: {skill_name}
type: auto_generated
source: tenant_{self.tenant_id}
created_at: {datetime.now().isoformat()}
---

# {title}

## 触发条件
用户需求包含以下关键词时使用：
- {title.split(':')[0] if ':' in title else title}

## 执行方式
根据成功经验执行对应脚本。
"""
            skill_path.write_text(skill_content, encoding='utf-8')
            generated.append(str(skill_path))
        return generated


def retrieve(tenant_id: int, query: str, use_vector: bool = True) -> str:
    """统一检索接口"""
    manager = MemoryManager(tenant_id)
    results, method = manager.retrieve(query, use_vector)
    return manager.format_context(results, method)


def generate_skills(tenant_id: int) -> List[str]:
    """生成 Skills"""
    gen = SkillGenerator(tenant_id)
    return gen.generate()


def get_stats(tenant_id: int) -> Dict:
    """获取统计"""
    p = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / "main" / "evolution"
    stats = {"learnings": 0, "successes": 0, "errors": 0}
    for name in ["LEARNINGS.md", "SUCCESSES.md", "ERRORS.md"]:
        f = p / name
        if f.exists():
            stats[name.replace('.md', '').lower()] = len(f.read_text().split('\n##'))
    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  memory_retriever_complete.py retrieve <tenant_id> <query> [--vector]")
        print("  memory_retriever_complete.py generate <tenant_id>")
        print("  memory_retriever_complete.py stats <tenant_id>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "retrieve" and len(sys.argv) >= 4:
        tenant = int(sys.argv[2])
        query = " ".join(sys.argv[3:])
        use_vector = "--vector" in query
        if use_vector:
            query = query.replace("--vector", "").strip()
        print(retrieve(tenant, query, use_vector))
    
    elif cmd == "generate" and len(sys.argv) >= 3:
        tenant = int(sys.argv[2])
        generated = generate_skills(tenant)
        if generated:
            print(f"✅ 生成 {len(generated)} 个 Skills:")
            for g in generated:
                print(f"   {g}")
        else:
            print("无新 Skills 需要生成")
    
    elif cmd == "stats" and len(sys.argv) >= 3:
        tenant = int(sys.argv[2])
        print(json.dumps(get_stats(tenant), indent=2))
