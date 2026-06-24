#!/usr/bin/env python3
"""Gateway 辅助函数 - 从主网关抽出的业务逻辑"""

import json
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


# ========== 用户状态管理 ==========

class ProjectUserState:
    """项目级用户状态"""

    def __init__(self, project_id: str = None, user_id: str = "default"):
        self.project_id = project_id
        self.user_id = user_id
        self._state: Dict[str, Any] = {}
        self._load()

    def _get_state_path(self) -> Path:
        if self.project_id:
            try:
                from core.lib.code_repo import get_code_repo
                repo = get_code_repo(self.user_id)
                project = repo.get_project(self.project_id)
                if project:
                    project_path = Path(project["path"])
                    state_dir = project_path / ".clawsjoy"
                    state_dir.mkdir(exist_ok=True)
                    return state_dir / "user_state.json"
            except Exception:
                pass
        state_dir = Path(f"data/user_states/{self.user_id}")
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "state.json"

    def _load(self):
        path = self._get_state_path()
        if path.exists():
            try:
                self._state = json.loads(path.read_text())
            except Exception:
                self._state = {}
        else:
            self._state = {}

    def _save(self):
        self._get_state_path().write_text(json.dumps(self._state, indent=2, ensure_ascii=False))

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def set(self, key: str, value):
        self._state[key] = value
        self._save()

    def get_all(self) -> Dict:
        return self._state.copy()


_USER_STATE_CACHE: Dict[str, ProjectUserState] = {}

def get_user_state(project_id: str = None, user_id: str = "default") -> Dict:
    key = f"{project_id or 'global'}_{user_id}"
    if key not in _USER_STATE_CACHE:
        _USER_STATE_CACHE[key] = ProjectUserState(project_id, user_id)
    return _USER_STATE_CACHE[key].get_all()

def set_user_state(project_id: str, user_id: str, key: str, value):
    state_key = f"{project_id or 'global'}_{user_id}"
    if state_key not in _USER_STATE_CACHE:
        _USER_STATE_CACHE[state_key] = ProjectUserState(project_id, user_id)
    _USER_STATE_CACHE[state_key].set(key, value)


# ========== 记忆管理 ==========

MEMORY_FILE = Path("data/memory_simple.json")
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_memories(user_id: str) -> list:
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        agent = MemoryAgentV4(user_id)
        result = agent.recall_forever("all_memories")
        if result:
            return result if isinstance(result, list) else [result]
    except Exception:
        pass

    if MEMORY_FILE.exists():
        all_memories = json.loads(MEMORY_FILE.read_text())
        return all_memories.get(user_id, [])
    return []

def save_memory(user_id: str, fact: str):
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        agent = MemoryAgentV4(user_id)
        agent.remember_forever("fact", fact)
        return
    except Exception:
        pass

    all_memories = {}
    if MEMORY_FILE.exists():
        all_memories = json.loads(MEMORY_FILE.read_text())
    memories = all_memories.get(user_id, [])
    memories.append({"fact": fact, "timestamp": datetime.now().isoformat()})
    all_memories[user_id] = memories[-100:]
    MEMORY_FILE.write_text(json.dumps(all_memories, indent=2))

def search_memories(user_id: str, query: str) -> list:
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        agent = MemoryAgentV4(user_id)
        result = agent.process(f"搜索记忆: {query}")
        if result and result.get("response"):
            return [result.get("response")]
    except Exception:
        pass

    memories = load_memories(user_id)
    results = []
    for m in memories:
        fact = m.get("fact", "")
        if query in fact or fact in query:
            results.append(fact)
    return results[:10]


# ========== 用户信息提取 ==========

def extract_user_info(message: str, user_id: str, project_id: str = None) -> bool:
    m = re.search(r'我叫([\u4e00-\u9fa5]{2,4})', message)
    if m:
        name = m.group(1)
        set_user_state(project_id, user_id, "user_name", name)
        save_memory(user_id, f"用户名字: {name}")
        return True
    return False

def answer_from_state(message: str, user_id: str, project_id: str = None) -> Optional[str]:
    if "我叫什么名字" in message or "我的名字" in message:
        state = get_user_state(project_id, user_id)
        name = state.get("user_name")
        if name:
            return f"您叫{name}呀，我记着呢！"
        memories = load_memories(user_id)
        for m in memories:
            fact = m.get("fact", "")
            if "用户名字:" in fact:
                return f"您叫{fact.replace('用户名字: ', '')}呀"
        return "您还没告诉我您的名字呢"
    return None


# ========== 文件内容读取 ==========

def extract_file_content(project_id: str, file_path: str, user_id: str) -> tuple:
    try:
        from core.lib.code_repo import get_code_repo
        repo = get_code_repo(user_id)
        content = repo.get_file_content(project_id, file_path)
        if content:
            return content, f"文件: {file_path} ({len(content)} 字符)"
        return "", "文件为空或不存在"
    except Exception as e:
        return "", f"读取失败: {e}"


# ========== 学习统计 ==========

LEARNING_FILE = Path("data/learning_data/learning_stats.json")
LEARNING_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_learning_stats() -> dict:
    if LEARNING_FILE.exists():
        data = json.loads(LEARNING_FILE.read_text())
        if isinstance(data, dict):
            if "total_learnings" not in data:
                data["total_learnings"] = data.get("learned", 0)
            return data
    return {"total_learnings": 0, "successful_learnings": 0, "failed_learnings": 0}

def record_learning(fact: str, success: bool = True):
    stats = load_learning_stats()
    stats["total_learnings"] = stats.get("total_learnings", 0) + 1
    if success:
        stats["successful_learnings"] = stats.get("successful_learnings", 0) + 1
    else:
        stats["failed_learnings"] = stats.get("failed_learnings", 0) + 1
    LEARNING_FILE.write_text(json.dumps(stats, indent=2))


# ========== 用户目录创建 ==========

def create_user_directories(username: str, user_id: str, email: str = ""):
    user_dir = Path(f"data/users/{username}")
    if user_dir.exists():
        return
    user_dir.mkdir(parents=True)
    for sub in ["encrypted", "workspace", "logs"]:
        (user_dir / sub).mkdir(parents=True, exist_ok=True)
    profile = {"user_id": user_id, "username": username, "email": email,
               "role": "user", "created_at": datetime.now().isoformat()}
    (user_dir / "profile.json").write_text(json.dumps(profile, indent=2))
