#!/usr/bin/env python3
"""记忆服务 Skill - 三层记忆系统"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MemoryService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.db_path = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/memory.db")
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS short_term (
                id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, created_at TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS long_term (
                id INTEGER PRIMARY KEY, key TEXT UNIQUE, value TEXT, updated_at TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS skill_memory (
                id INTEGER PRIMARY KEY, skill_name TEXT, success_count INTEGER, last_used TIMESTAMP, params TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_short_term(self, session_id: str, role: str, content: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO short_term (session_id, role, content, created_at) VALUES (?, ?, ?, ?)',
                  (session_id, role, content, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_short_term(self, session_id: str, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT role, content FROM short_term WHERE session_id = ? ORDER BY created_at DESC LIMIT ?',
                  (session_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{'role': r[0], 'content': r[1]} for r in reversed(rows)]
    
    def set_long_term(self, key: str, value: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO long_term (key, value, updated_at) VALUES (?, ?, ?)',
                  (key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_long_term(self, key: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT value FROM long_term WHERE key = ?', (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None

def execute(params: Dict) -> Dict:
    """Skill 执行入口"""
    action = params.get('action')
    tenant_id = params.get('tenant_id', '1')
    session_id = params.get('session_id', 'default')
    
    service = MemoryService(tenant_id)
    
    if action == 'add':
        service.add_short_term(session_id, params.get('role', 'user'), params.get('content', ''))
        return {'success': True}
    elif action == 'get':
        memories = service.get_short_term(session_id, params.get('limit', 10))
        return {'success': True, 'memories': memories}
    elif action == 'set_pref':
        service.set_long_term(params.get('key', ''), params.get('value', ''))
        return {'success': True}
    elif action == 'get_pref':
        value = service.get_long_term(params.get('key', ''))
        return {'success': True, 'value': value}
    else:
        return {'success': False, 'error': f'Unknown action: {action}'}
