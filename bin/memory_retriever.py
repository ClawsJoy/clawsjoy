#!/usr/bin/env python3
import sys, re
from pathlib import Path

CLAWSJOY_ROOT = Path("/root/clawsjoy")
TENANTS_ROOT = CLAWSJOY_ROOT / "tenants"

def load_memories(tenant_id):
    p = TENANTS_ROOT / f"tenant_{tenant_id}" / "agents" / "main" / "evolution" / "LEARNINGS.md"
    return p.read_text(encoding='utf-8') if p.exists() else ""

def retrieve(tenant_id, query):
    text = load_memories(tenant_id)
    if not text:
        return "无记忆"
    kw = [w for w in re.findall(r'[\u4e00-\u9fa5]{2,}', query) if len(w) > 1]
    if not kw:
        return "无关键词"
    sections = re.split(r'\n##\s+', text)
    results = []
    for sec in sections:
        if not sec.strip():
            continue
        score = sum(1 for k in kw if k in sec)
        if score:
            title = sec.split('\n')[0]
            results.append({"title": title, "content": sec[:300], "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    if not results:
        return "未找到相关记忆"
    out = f"\n## 📚 相关历史经验\n\n"
    for i, r in enumerate(results[:3], 1):
        out += f"### {i}. {r['title']}\n{r['content']}\n\n"
    return out

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "retrieve":
        print(retrieve(int(sys.argv[2]), " ".join(sys.argv[3:])))
    else:
        print("用法: memory_retriever.py retrieve <tenant_id> <query>")
