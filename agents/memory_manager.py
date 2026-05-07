"""三层记忆系统：Qdrant 向量检索 + SQLite 结构化 + JSON 兜底"""

import json
import sqlite3
import requests
import hashlib
from pathlib import Path
from datetime import datetime

class MemoryManager:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.qdrant_url = "http://localhost:6333"
        self.collection = f"mem_{tenant_id}"
        self.db_path = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/memory.db")
        self.json_path = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/memory.json")
        self._init()
    
    def _init(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, text TEXT, type TEXT, created_at TEXT)")
        conn.close()
        
        try:
            requests.put(f"{self.qdrant_url}/collections/{self.collection}", json={
                "vectors": {"size": 384, "distance": "Cosine"}
            })
        except:
            pass
    
    def _vector(self, text):
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        return [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, 16, 2)] + [0.0] * (384 - 8)
    
    def add(self, text, type="interaction"):
        # Qdrant
        try:
            requests.put(f"{self.qdrant_url}/collections/{self.collection}/points", json={
                "points": [{"id": abs(hash(text)) % 10**9, "vector": self._vector(text), "payload": {"text": text, "type": type}}]
            })
        except:
            pass
        # SQLite
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO memories (text, type, created_at) VALUES (?, ?, ?)", (text, type, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        # JSON
        data = []
        if self.json_path.exists():
            with open(self.json_path) as f:
                data = json.load(f)
        data.append({"text": text, "type": type, "time": datetime.now().isoformat()})
        with open(self.json_path, 'w') as f:
            json.dump(data[-100:], f, indent=2)
    
    def search(self, query, limit=5):
        try:
            resp = requests.post(f"{self.qdrant_url}/collections/{self.collection}/points/search", json={
                "vector": self._vector(query), "limit": limit, "with_payload": True
            })
            if resp.status_code == 200:
                return [p["payload"]["text"] for p in resp.json().get("result", [])]
        except:
            pass
        # 降级 SQLite
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT text FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
        results = [row[0] for row in cur.fetchall()]
        conn.close()
        return results
