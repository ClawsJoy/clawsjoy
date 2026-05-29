import logging

"""方言 Agent - 自动学习"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter
from core.lib.workspace_manager import workspace_manager


class DialectAgent(SmartAgent):
    """方言学习翻译助手 - 自动学习"""

    name = "dialect_agent"
    description = "方言学习翻译助手"
    type = "custom"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("dialect_agent")
        self.profile = self._load_profile()
        self.dialect_config = self._load_config()
        print(f"🗣️ 方言Agent 初始化完成")

    def _load_config(self) -> dict:
        """加载方言配置"""
        import yaml
        config_file = Path("config/dialect_learning.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_profile(self) -> dict:
        """加载用户画像"""
        profile_file = Path(f"data/users/{self.user_id}/dialect_profile.json")
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                return json.load(f)
        return {
            "user_id": self.user_id,
            "location": None,
            "dialect": None,
            "learned_words": {},
            "usage_count": {},
            "history": []
        }

    def _save_profile(self):
        """保存用户画像"""
        profile_file = Path(f"data/users/{self.user_id}/dialect_profile.json")
        profile_file.parent.mkdir(parents=True, exist_ok=True)
        self.profile["updated_at"] = datetime.now().isoformat()
        with open(profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)

    def _set_location(self, location: str):
        """设置用户地点，自动识别方言"""
        self.profile["location"] = location
        
        # 从配置中查找方言
        province_map = self.dialect_config.get("province_mapping", {})
        for province, dialect in province_map.items():
            if province in location or location in province:
                self.profile["dialect"] = dialect
                print(f"📍 识别方言: {location} → {dialect}")
                break
        
        self._save_profile()
        return self.profile.get("dialect")

    def _learn_word(self, dialect: str, standard: str, context: str = ""):
        """学习方言词"""
        if dialect not in self.profile["learned_words"]:
            self.profile["learned_words"][dialect] = {
                "standard": standard,
                "learned_at": datetime.now().isoformat(),
                "context": context,
                "usage_count": 0,
                "mastered": False
            }
            self.profile["history"].append({
                "action": "learn",
                "dialect": dialect,
                "standard": standard,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.profile["learned_words"][dialect]["usage_count"] += 1
            if self.profile["learned_words"][dialect]["usage_count"] >= 3:
                self.profile["learned_words"][dialect]["mastered"] = True
        
        self._save_profile()
        print(f"📚 学习方言: {dialect} → {standard}")

    def _auto_learn_from_text(self, text: str):
        """从文本中自动学习"""
        # 检测可能的方言词
        all_dialects = []
        for dialect_info in self.dialect_config.get("dialects", {}).values():
            for word_info in dialect_info.get("common_words", []):
                dialect = word_info["dialect"]
                standard = word_info["standard"]
                if dialect in text:
                    all_dialects.append((dialect, standard))
        
        # 自动学习
        for dialect, standard in all_dialects:
            # 增加使用计数
            if dialect in self.profile["usage_count"]:
                self.profile["usage_count"][dialect] += 1
            else:
                self.profile["usage_count"][dialect] = 1
            
            # 使用3次后自动学习
            if self.profile["usage_count"][dialect] >= 3 and dialect not in self.profile["learned_words"]:
                self._learn_word(dialect, standard, f"自动学习(使用{self.profile['usage_count'][dialect]}次)")
        
        self._save_profile()

    def _translate(self, text: str) -> str:
        """翻译方言"""
        result = text
        
        # 使用已学习的词
        for dialect, info in self.profile["learned_words"].items():
            if dialect in result:
                result = result.replace(dialect, info["standard"])
        
        # 如果还有未识别的，用 LLM 辅助
        if result == text:
            prompt = f"请将以下方言翻译成普通话：{text}"
            try:
                llm_result = smart_adapter.generate(prompt, auto_select=True)
                if llm_result:
                    result = llm_result
            except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
                pass
        
        return result

    def process(self, user_input: str, context=None) -> Dict:
        print(f"[方言] 收到: {user_input}")
        
        # 1. 设置地点（如"我在XX"）
        location_match = re.search(r'我在([\u4e00-\u9fa5]{2,})', user_input)
        if location_match:
            location = location_match.group(1)
            dialect = self._set_location(location)
            return {
                "success": True,
                "response": f"已识别您的位置: {location}，方言: {dialect or '待学习'}",
                "agent": self.name,
                "user_id": self.user_id
            }
        
        # 2. 学习方言（如"学习'XX'意思是'YY'"）
        learn_match = re.search(r'学习[\'\"](.+?)[\'\"]意思(?:是)?[\'\"](.+?)[\'\"]', user_input)
        if learn_match:
            dialect = learn_match.group(1)
            standard = learn_match.group(2)
            self._learn_word(dialect, standard, "明确教学")
            return {
                "success": True,
                "response": f"已学习: {dialect} 意思是 {standard}",
                "agent": self.name,
                "user_id": self.user_id
            }
        
        # 3. 自动学习（从对话中）
        self._auto_learn_from_text(user_input)
        
        # 4. 翻译
        translated = self._translate(user_input)
        
        return {
            "success": True,
            "response": translated,
            "agent": self.name,
            "user_id": self.user_id
        }


dialect_agent = DialectAgent()

