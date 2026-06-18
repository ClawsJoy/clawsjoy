#!/usr/bin/env python3
"""DialectAgent v4.2 - 精简稳定版（方言助手 - 能说能学）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class DialectAgentV4(BusinessAgent):
    """方言 Agent - 精简稳定版（支持学习新方言）"""

    name = "dialect_agent_v4"
    description = "智慧方言助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.user_id = user_id
        self._dialect_db = self._load_dialect_db()
        print(f"🗣 DialectAgent v{self.version} 启动")
        print(f"   📚 已加载 {len(self._dialect_db)} 条方言知识")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        # 学习方言：用户教方言
        if any(kw in t for kw in ["就是", "意思是", "指的是", "叫"]) and "方言" in t:
            return self._learn_dialect(user_input)
        
        # 查询方言
        if any(kw in t for kw in ["怎么说", "怎么讲", "方言", "用方言"]):
            return self._translate_to_dialect(user_input)
        
        # 列出已学方言
        if any(kw in t for kw in ["列出方言", "已学方言", "方言列表"]):
            return self._list_dialects()
        
        return self._resp("🗣 输入「你好用方言怎么说」、「方言 开心 就是 高兴」或「列出方言」")

    # ================================================================
    #  学习方言
    # ================================================================

    def _learn_dialect(self, user_input: str) -> Dict:
        """学习新方言表达"""
        # 格式1: 方言 开心 就是 高兴
        match = re.search(r'(?:方言|用方言)\s*(.+?)\s+(?:就是|意思是|指的是|叫)\s+(.+)', user_input)
        if match:
            word, meaning = match.group(1).strip(), match.group(2).strip()
            self._save_dialect(word, meaning)
            return self._resp(f"✅ 学会啦！「{word}」就是「{meaning}」的意思~ 😊")
        
        # 格式2: 开心用方言怎么说
        match = re.search(r'(.+?)\s*(?:用方言怎么说|怎么用方言说|方言怎么说)', user_input)
        if match:
            word = match.group(1).strip()
            meaning = self._lookup_dialect(word)
            if meaning:
                return self._resp(f"🗣 「{word}」用方言说就是「{meaning}」~")
            # 如果不知道，用 LLM 生成
            result = self._call_llm(f"用方言（四川话/东北话/广东话）表达「{word}」，只输出结果")
            if result:
                self._save_dialect(word, result.strip())
                return self._resp(f"🗣 「{word}」用方言说就是「{result.strip()}」~ 我记住啦！")
            return self._resp(f"🤔 我不太确定「{word}」的方言说法，你可以教我吗？格式：方言 {word} 就是 xxx")
        
        return self._resp("🗣 格式：方言 开心 就是 高兴 或者 开心用方言怎么说")

    # ================================================================
    #  翻译到方言
    # ================================================================

    def _translate_to_dialect(self, user_input: str) -> Dict:
        """翻译成方言"""
        word = re.sub(r'(怎么说|怎么讲|方言|用方言)', '', user_input).strip()
        if not word:
            return self._resp("请说：你好用方言怎么说")
        
        # 查本地数据库
        meaning = self._lookup_dialect(word)
        if meaning:
            return self._resp(f"🗣 「{word}」用方言说就是「{meaning}」~")
        
        # 用 LLM 生成
        result = self._call_llm(f"用方言（四川话/东北话/广东话）表达「{word}」，只输出结果")
        if result:
            self._save_dialect(word, result.strip())
            return self._resp(f"🗣 「{word}」用方言说就是「{result.strip()}」~ 我记住啦！")
        
        return self._resp(f"🤔 我不太确定「{word}」的方言说法，你可以教我吗？格式：方言 {word} 就是 xxx")

    # ================================================================
    #  列出方言
    # ================================================================

    def _list_dialects(self) -> Dict:
        if not self._dialect_db:
            return self._resp("📭 还没有学会方言，你可以教我！格式：方言 开心 就是 高兴")
        
        lines = ["🗣 已学方言："]
        for word, meaning in list(self._dialect_db.items())[:20]:
            lines.append(f"  • {word} → {meaning}")
        if len(self._dialect_db) > 20:
            lines.append(f"  ... 还有 {len(self._dialect_db) - 20} 条")
        return self._resp("\n".join(lines))

    # ================================================================
    #  数据库操作
    # ================================================================

    def _load_dialect_db(self) -> Dict:
        """加载方言数据库"""
        path = Path(f"data/dialects/{self.user_id}.json")
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_dialect_db(self):
        """保存方言数据库"""
        path = Path(f"data/dialects/{self.user_id}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._dialect_db, f, ensure_ascii=False, indent=2)

    def _save_dialect(self, word: str, meaning: str):
        """保存一条方言"""
        self._dialect_db[word] = meaning
        self._save_dialect_db()

    def _lookup_dialect(self, word: str) -> Optional[str]:
        """查询方言"""
        return self._dialect_db.get(word)

    # ================================================================
    #  辅助
    # ================================================================

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 100}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[Dialect] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = DialectAgentV4("test")
    print(agent.process("方言 开心 就是 高兴")["response"])
