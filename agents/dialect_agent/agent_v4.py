#!/usr/bin/env python3
"""dialect_agent v4.0 - 对话级方言大师（集成用户画像）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


# 简单的用户画像管理（避免循环导入）
class SimpleUserProfile:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._path = Path(f"data/profile/{user_id}.json")
        self._load()
    
    def _load(self):
        if self._path.exists():
            try:
                with open(self._path, 'r') as f:
                    self.data = json.load(f)
            except:
                self._init_data()
        else:
            self._init_data()
    
    def _init_data(self):
        self.data = {
            "user_id": self.user_id,
            "dialect": {
                "name": "方言",
                "words": {},
                "phrases": {}
            }
        }
    
    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, 'w') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_dialect_name(self) -> str:
        return self.data.get("dialect", {}).get("name", "方言")
    
    def set_dialect_name(self, name: str):
        self.data["dialect"]["name"] = name
        self._save()
    
    def get_words(self) -> Dict:
        return self.data.get("dialect", {}).get("words", {})
    
    def add_word(self, dialect: str, standard: str):
        self.data["dialect"]["words"][dialect] = standard
        self._save()


class DialectAgentV4(BusinessAgent):
    """方言大师 - 集成用户画像"""
    
    name = "dialect_agent_v4"
    description = "方言大师"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.user_id = user_id
        self._profile = SimpleUserProfile(user_id)
        print(f"🗣️ 方言大师 v{self.version}")
        print(f"   👤 用户: {user_id}")
        print(f"   🌍 方言: {self._profile.get_dialect_name()}")
        print(f"   📚 已学: {len(self._profile.get_words())} 个词")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.90) if action == "convert" and target == "dialect" else (False, 0.0)
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 1. 设置方言名称
        if "设置方言" in user_input:
            match = re.search(r'设置方言[：:]\s*(.+)', user_input)
            if match:
                name = match.group(1).strip()
                self._profile.set_dialect_name(name)
                return self._response(f"✅ 已设置方言：{name}")
        
        # 2. 学习方言
        if "学习方言" in user_input:
            match = re.search(r'学习方言\s*(.+?)\s*[=＝]\s*(.+)', user_input)
            if match:
                dialect, standard = match.group(1).strip(), match.group(2).strip()
                self._profile.add_word(dialect, standard)
                return self._response(f"✅ 已学习：{dialect} = {standard}")
        
        # 3. 查看已学
        if "我的方言" in user_input or "已学" in user_input:
            words = self._profile.get_words()
            if not words:
                return self._response(f"还没有学习{self._profile.get_dialect_name()}词。\n\n教我：学习方言 阿拉 = 我们")
            
            lines = [f"📚 **{self._profile.get_dialect_name()}词库**"]
            for d, s in words.items():
                lines.append(f"  • {d} = {s}")
            return self._response("\n".join(lines))
        
        # 4. 方言转换
        if any(kw in user_input for kw in ["转换成", "翻译成", "怎么说"]):
            content = re.sub(r'转换成|翻译成|怎么说', '', user_input)
            content = re.sub(r'宁波话|四川话|方言', '', content).strip()
            
            if content:
                words = self._profile.get_words()
                result = content
                for dialect, standard in words.items():
                    result = result.replace(standard, dialect)
                
                if result != content:
                    return self._response(f"🗣️ **{self._profile.get_dialect_name()}**\n\n{content}\n↓\n{result}")
                else:
                    return self._response(f"🗣️ 暂未学习「{content}」的{self._profile.get_dialect_name()}表达\n\n教我：学习方言 {content}的方言 = ?")
        
        return self._response(self._get_help())
    
    def _get_help(self) -> str:
        name = self._profile.get_dialect_name()
        return f"""🗣️ **{name}大师**

📖 **教方盲**：学习方言 阿拉 = 我们
🏷️ **起名字**：设置方言：{name}
🔄 **翻译**：转换成{name} 我们回家
📋 **查词库**：我的方言"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = DialectAgentV4("test")
    print("✅ dialect_agent_v4 测试通过")
