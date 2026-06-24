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
        self._summary: str = ""             # 早期对话摘要
        self._total_turns = 0
    
    # ========== 滑动窗口 ==========
    
    def add_turn(self, user: str, assistant: str, action: str, extracted: Dict):
        """添加一轮对话"""
        self._total_turns += 1
        self._window.append({
            "user": user[:200], "assistant": assistant[:200],
            "action": action, "extracted": extracted
        })
        # 保持窗口大小
        if len(self._window) > self.MAX_WINDOW:
            removed = self._window.pop(0)
            # 被移除的轮次加入摘要
            self._summary = self._summarize_old(removed, self._summary)
        
        # 触发完整摘要
        if self._total_turns > self.SUMMARY_TRIGGER and self._total_turns % 5 == 0:
            self._compact()
    
    def _summarize_old(self, removed: Dict, current_summary: str) -> str:
        """将被移除的轮次压缩进摘要"""
        parts = []
        if current_summary:
            parts.append(current_summary)
        user = removed.get("user", "")[:80]
        action = removed.get("action", "")
        ext = removed.get("extracted", {})
        if ext:
            parts.append(f"用户说: {user}")
        else:
            parts.append(f"用户: {user} | 动作: {action}")
        return " | ".join(parts[-5:])  # 只保留最近5条摘要
    
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
        
        return "\n".join(parts) if parts else ""
    
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
        self._summary = ""
        self._total_turns = 0


# 全局实例（按用户）
_managers: Dict[str, ContextManager] = {}

def get_context(user_id: str = "default") -> ContextManager:
    if user_id not in _managers:
        _managers[user_id] = ContextManager()
    return _managers[user_id]
