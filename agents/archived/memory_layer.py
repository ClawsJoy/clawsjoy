#!/usr/bin/env python3
"""三层记忆自动集成 - 给 TenantAgent 使用"""

import json
import sqlite3
import requests
import hashlib
from pathlib import Path
from datetime import datetime

class AutoMemory:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.qdrant_url = "http://localhost:6333"
        self.db_path = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/memory.db")
        self.json_path = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/memory.json")
        self._init_db()
        self._init_qdrant()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, text TEXT, created_at TEXT, type TEXT)")
        conn.close()
    
    def _init_qdrant(self):
        try:
            requests.put(f"{self.qdrant_url}/collections/{self.tenant_id}", json={
                "vectors": {"size": 384, "distance": "Cosine"},
                "hnsw_config": {"m": 16, "ef_construct": 100}
            })
        except:
            pass
    
    def _simple_vector(self, text):
        """简单向量（实际可用 embedding 模型，这里用 hash 模拟）"""
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        return [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, 16, 2)] + [0.0] * (384 - 8)
    
    def remember(self, text, type="interaction"):
        """自动分级记忆"""
        # 1. Qdrant 长期记忆
        try:
            vector = self._simple_vector(text)
            requests.put(f"{self.qdrant_url}/collections/{self.tenant_id}/points", json={
                "points": [{
                    "id": hash(text) % 10**9,
                    "vector": vector,
                    "payload": {"text": text, "type": type, "time": datetime.now().isoformat()}
                }]
            })
        except:
            pass
        # 2. SQLite 结构化记忆
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO events (text, created_at, type) VALUES (?, ?, ?)",
                     (text, datetime.now().isoformat(), type))
        conn.commit()
        conn.close()
        # 3. JSON 兜底
        data = []
        if self.json_path.exists():
            data = json.load(open(self.json_path))
        data.append({"text": text, "type": type, "time": str(__import__("time").time())})
        json.dump(data[-200:], open(self.json_path, "w"))
    
    def recall(self, query, limit=5):
        """自动回忆关联记忆"""
        try:
            vector = self._simple_vector(query)
            resp = requests.post(f"{self.qdrant_url}/collections/{self.tenant_id}/points/search", json={
                "vector": vector, "limit": limit, "with_payload": True
            }, timeout=3)
            if resp.status_code == 200:
                hits = resp.json().get("result", [])
                return [h["payload"]["text"] for h in hits if "text" in h["payload"]]
        except:
            pass
        # 降级 SQLite
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT text FROM events ORDER BY created_at DESC LIMIT ?", (limit,))
        results = [row[0] for row in cur.fetchall()]
        conn.close()
        return results
    
    def recall_by_keyword(self, keyword, limit=3):
        """按关键词回忆（配合 Meilisearch）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT text FROM events WHERE text LIKE ? ORDER BY created_at DESC LIMIT ?",
                           (f"%{keyword}%", limit))
        results = [row[0] for row in cur.fetchall()]
        conn.close()
        return results

# 自动挂载到 TenantAgent（如果存在）
try:
    from tenant_agent import TenantAgent
    def _patched_init(self, tenant_id):
        self._old_init(tenant_id)
        self.memory = AutoMemory(tenant_id)
    
    def patched_chat(self, user_input):
        # 先回忆
        context = self.memory.recall(user_input, limit=2)
        if context:
            print(f"📚 自动回忆: {context}")
        return self._old_chat(user_input)
    
    TenantAgent._old_init = TenantAgent.__init__
    TenantAgent.__init__ = _patched_init
    TenantAgent._old_chat = TenantAgent.chat
    TenantAgent.chat = patched_chat
    print("✅ 记忆层已自动注入 TenantAgent")
except:
    pass

def clean_old_memories(self, days=30):
    """清理 30 天前的记忆（Qdrant + SQLite）"""
    import time
    expire_time = time.time() - days * 86400
    # Qdrant 不支持按时间删除，这里只清理 SQLite
    conn = sqlite3.connect(self.db_path)
    conn.execute("DELETE FROM events WHERE created_at < datetime('now', ?)", (f'-{days} days',))
    conn.commit()
    conn.close()
    # JSON 兜底保留最近 100 条
    if self.json_path.exists():
        data = json.load(open(self.json_path))
        json.dump(data[-100:], open(self.json_path, "w"))
    print(f"🧹 已清理 {days} 天前的记忆")

# 每天凌晨 3 点自动清理
def auto_clean(self):
    import subprocess
    subprocess.run(["python3", "-c", f"from agents.memory_layer import AutoMemory; AutoMemory('{self.tenant_id}').clean_old_memories()"])

def recall_with_weight(self, query, limit=5, weight_threshold=0.5):
    """按权重回忆（高频记忆优先）"""
    conn = sqlite3.connect(self.db_path)
    cur = conn.execute("""
        SELECT text, COUNT(*) as cnt
        FROM events
        WHERE text LIKE ?
        GROUP BY text
        ORDER BY cnt DESC, created_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))
    results = [row[0] for row in cur.fetchall() if row[1] >= weight_threshold]
    conn.close()
    return results
