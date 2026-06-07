#!/usr/bin/env python3
"""Base - Base 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from core.lib import config_helper


class BaseAgent:
    """Agent 基类"""

    def __init__(self, name: str, user_id: str = "default"):
        self.name = name
        self.user_id = user_id

        # 初始化目录
        self.data_dir = Path(
            f"{config_helper.get_data_root()}/v5/users/{self.user_id}/agents/{self.name}"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.data_dir / "memory.json"

        # 加载记忆
        self._load_memory()

        print(f"✓ {name} 已启动")

    def _load_memory(self):
        """加载记忆"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    self.memory = json.load(f)
            except Exception as e:
                self.memory = self._init_memory()
        else:
            self.memory = self._init_memory()

    def _init_memory(self) -> Dict:
        """初始化记忆"""
        return {
            "preferences": {},
            "history": [],
            "stats": {
                "total_interactions": 0,
                "created_at": datetime.now().isoformat(),
            },
        }

    def _save_memory(self):
        """保存记忆"""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def _build_prompt(self, user_input: str, system_prompt: str = None) -> str:
        """构建提示词"""
        if system_prompt:
            return f"""{system_prompt}

用户偏好: {self.memory.get('preferences', {})}

用户: {user_input}"""

        return f"""你是 {self.name}。

用户偏好: {self.memory.get('preferences', {})}

请用中文回答，温暖、专业。

用户: {user_input}
{self.name}:"""

    def remember_preference(self, key: str, value: Any):
        """记住偏好"""
        self.memory["preferences"][key] = value
        self._save_memory()

    def recall_preference(self, key: str) -> Any:
        """回忆偏好"""
        return self.memory["preferences"].get(key)

    def record_history(self, user_input: str, response: str):
        """记录历史"""
        self.memory["history"].append(
            {
                "user": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )
        if len(self.memory["history"]) > 50:
            self.memory["history"] = self.memory["history"][-50:]
        self._save_memory()

    def update_stats(self):
        """更新统计"""
        self.memory["stats"]["total_interactions"] = (
            self.memory["stats"].get("total_interactions", 0) + 1
        )
        self._save_memory()

    def process(self, user_input: str) -> Dict:
        """处理消息 - 子类实现"""
        raise NotImplementedError
