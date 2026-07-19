#!/usr/bin/env python3
"""上下文管理器 - 滑动窗口+摘要+实体缓存"""

import json
from typing import Dict, List, Optional


class ContextManager:
    """上下文管理器：滑动窗口8轮 + 摘要压缩 + 实体缓存"""
    
    MAX_WINDOW = 8           # 保留最近8轮完整对话
    MAX_ENTITIES = 20        # 最多缓存20个实体
    SUMMARY_TRIGGER = 12     # 超过12轮触发摘要
    
    def __init__(self):
        self._window: List[Dict] = []      # 滑动窗口
        self._entities: Dict[str, str] = {}  # 实体缓存 {名字: john, 邮箱: xx@xx, ...}
        self._world_model: dict = {}
        self._summary: dict = {
            "task_goal": "",
            "completed": [],
            "in_progress": "",
            "failed_attempts": [],
            "key_findings": [],
            "file_status": {}
        }  # 结构化早期对话摘要
        self._total_turns = 0
    
    # ========== 滑动窗口 ==========
    
    def add_turn(self, user: str, assistant: str, action: str, extracted: Dict, world_model: dict = None, last_task_pattern: dict = None, intent_model: dict = None):
        """添加一轮对话"""
        self._total_turns += 1
        self._window.append({
            "user": user[:200], "assistant": assistant[:200],
            "action": action, "extracted": extracted,
            "world_model": world_model,
            "last_task_pattern": last_task_pattern,
            "intent_model": intent_model,  # 新增
        })
        if world_model:
            self._world_model = world_model
        if last_task_pattern:
            self._last_task_pattern = last_task_pattern
        if intent_model:
            self._intent_model = intent_model  # 新增
        # 保持窗口大小
        if len(self._window) > self.MAX_WINDOW:
            removed = self._window.pop(0)
            # 被移除的轮次加入摘要
            self._summary = self._summarize_old(removed, self._summary)
        
        # 触发完整摘要
        if self._total_turns > self.SUMMARY_TRIGGER and self._total_turns % 5 == 0:
            self._compact()
    
    def _summarize_old(self, removed: Dict, current_summary: dict) -> dict:
        """将被移除的轮次按字段分类存储进摘要。代码块和用户指令不压缩。"""
        user_msg = removed.get("user", "")
        assistant_msg = removed.get("assistant", "")
        
        # 资产保护：包含代码块或用户具体指令的消息不压缩
        if "```" in user_msg or "```" in assistant_msg:
            return current_summary
        if any(kw in user_msg for kw in ["写入以下", "替换为", "用 write_file", "完整代码"]):
            return current_summary
        
        action = removed.get("action", "")
        ext = removed.get("extracted", {})
        user_msg = user_msg[:200]

        # 按 action 类型分类存储
        if action in ("task_goal", "create_file", "fix", "rebuild", "rewrite"):
            current_summary["task_goal"] = user_msg[:200]
        if action in ("write_file", "edit_file", "execute_command") and ext.get("success"):
            step = ext.get("desc", action)
            if step not in current_summary["completed"]:
                current_summary["completed"].append(step)
                if len(current_summary["completed"]) > 10:
                    current_summary["completed"] = current_summary["completed"][-10:]
        if action in ("write_file", "execute_command") and not ext.get("success"):
            fail = ext.get("error", action)
            if fail not in current_summary["failed_attempts"]:
                current_summary["failed_attempts"].append(fail)
                if len(current_summary["failed_attempts"]) > 5:
                    current_summary["failed_attempts"] = current_summary["failed_attempts"][-5:]
        elif action == "finding" or ext.get("finding"):
            finding = ext.get("finding", user_msg[:100])
            if finding not in current_summary["key_findings"]:
                current_summary["key_findings"].append(finding)
                if len(current_summary["key_findings"]) > 10:
                    current_summary["key_findings"] = current_summary["key_findings"][-10:]
        elif action == "file_status" or ext.get("file"):
            fname = ext.get("file", "")
            fstat = ext.get("status", "modified")
            current_summary["file_status"][fname] = fstat
        # 保留最新的 world_model
        _wm = removed.get("world_model")
        if _wm:
            current_summary["world_model"] = _wm
        # 更新项目结构快照（压缩时顺手更新）
        import os as _os2
        _proj_root = _os2.path.join("clawsjoy_dev")  # 默认项目根目录
        _struct = {}
        for _dir in ["services", "ui", "models", "utils"]:
            _path = _os2.path.join(_proj_root, _dir)
            if _os2.path.exists(_path):
                _struct[_dir] = sorted([f for f in _os2.listdir(_path) if f.endswith(".py") and f != "__pycache__"])
        if _os2.path.exists(_os2.path.join(_proj_root, "config.py")):
            _struct["config"] = "config.py"
        if _os2.path.exists(_os2.path.join(_proj_root, "app.py")):
            _struct["entry"] = "app.py"
        current_summary["project_structure"] = _struct
        if action and "in_progress" in action:
            current_summary["in_progress"] = user_msg[:200]

        return current_summary
    
    def _compact(self):
        """压缩早期窗口为摘要"""
        if len(self._window) <= 4:
            return
        # 保留最近4轮，更早的压缩
        to_compress = self._window[:-4]
        self._window = self._window[-4:]
        for item in to_compress:
            self._summary = self._summarize_old(item, self._summary)
    
    # ========== 实体缓存 ==========
    
    def update_entity(self, key: str, value: str):
        """更新实体缓存"""
        if key and value and len(value) < 100:
            self._entities[key] = value
            if len(self._entities) > self.MAX_ENTITIES:
                # 移除最旧的
                self._entities.pop(next(iter(self._entities)))
    
    def get_entity(self, key: str) -> Optional[str]:
        """获取实体"""
        return self._entities.get(key)
    
    def get_all_entities(self) -> Dict[str, str]:
        return dict(self._entities)
    
    # ========== 上下文注入 ==========
    
    def inject(self) -> str:
        """生成注入prompt的上下文片段"""
        parts = []
        
        # 1. 摘要（早期对话）
        if self._summary:
            parts.append(f"【早期对话】{self._summary}")
        
        # 2. 最近对话
        if self._window:
            lines = []
            for item in self._window[-4:]:  # 只取最近4轮
                ext = item.get("extracted", {})
                if ext:
                    lines.append(f"用户: {item['user'][:80]} → {item['action']}({json.dumps(ext, ensure_ascii=False)[:60]})")
                else:
                    lines.append(f"用户: {item['user'][:80]} → {item['action']}")
            parts.append("【最近对话】\n" + "\n".join(lines))
        
        # 3. 实体
        if self._entities:
            entities_str = ", ".join(f"{k}={v}" for k, v in list(self._entities.items())[:10])
            parts.append(f"【已知信息】{entities_str}")
        
        if not self._summary.get("task_goal") and not self._summary.get("completed"):
            return ""

        # 结构化输出，方便 Agent 快速恢复状态
        import json as _json
        structured = {
            **self._summary,
            "recent_turns": [
                {"user": item["user"][:80], "action": item["action"]}
                for item in self._window[-4:]
            ],
            "entities": dict(list(self._entities.items())[:10]),
            "total_turns": self._total_turns,
            "world_model": {k: v for k, v in getattr(self, '_world_model', {}).items() if v.get("status") != "path_mismatch"} if getattr(self, '_world_model', None) else None,
            "world_model_updated": getattr(self, '_world_model', {}).get("last_updated", "未知") if getattr(self, '_world_model', None) else None,
            "last_task_pattern": getattr(self, '_last_task_pattern', None),
            "intent_model": getattr(self, '_intent_model', None),  # 新增
        }
        return _json.dumps(structured, ensure_ascii=False)
    def clear(self):
        self._window.clear()
        self._entities.clear()
        self._summary = {
            "task_goal": "",
            "completed": [],
            "in_progress": "",
            "failed_attempts": [],
            "key_findings": [],
            "file_status": {}
        }
        self._total_turns = 0

    
    def resolve_reference(self, text: str) -> str:
        """指代消解：用实体缓存替换指代词"""
        if any(w in text for w in ["那个", "这个", "刚才", "它"]):
            # 从最近的实体中找
            for key, value in reversed(list(self._entities.items())):
                if len(value) > 2 and key not in ["名字", "姓名"]:
                    text = text.replace("那个", value).replace("这个", value)
                    break
        return text
    
    def clear(self):
        self._window.clear()
        self._entities.clear()
        self._summary = {
            "task_goal": "",
            "completed": [],
            "in_progress": "",
            "failed_attempts": [],
            "key_findings": [],
            "file_status": {}
        }
        self._total_turns = 0


# 全局实例（按用户）
_managers: Dict[str, ContextManager] = {}

def get_context(user_id: str = "default") -> ContextManager:
    if user_id not in _managers:
        _managers[user_id] = ContextManager()
    return _managers[user_id]
