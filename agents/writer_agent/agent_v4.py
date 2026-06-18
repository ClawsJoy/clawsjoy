#!/usr/bin/env python3
"""WriterAgent v4.2 - 精简稳定版（保留小说创作核心能力）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List

from core.agents.business.business_agent import BusinessAgent


class WriterAgentV4(BusinessAgent):
    """写作 Agent - 精简稳定版"""

    name = "writer_agent_v4"
    description = "智能写作助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._session_id = None
        self._novel = {
            "title": "",
            "outline": "",
            "chapters": [],
            "characters": [],
            "current_chapter": 0,
            "status": "idle"
        }
        self._llm_model = "qwen2.5:7b"
        self._max_retries = 2
        print(f"✍️ WriterAgent v{self.version} 启动")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
        return super().process(user_input, context)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        intent = self._detect_intent(user_input)
        
        handlers = {
            "start_novel": self._handle_start_novel,
            "continue": self._handle_continue,
            "new_chapter": self._handle_new_chapter,
            "modify": self._handle_modify,
            "character": self._handle_character,
            "outline": self._handle_outline,
            "complete": self._handle_complete,
            "write": self._handle_write,
            "polish": self._handle_polish,
        }
        
        handler = handlers.get(intent, self._handle_write)
        return handler(user_input, context)

    # ================================================================
    #  意图检测
    # ================================================================

    def _detect_intent(self, text: str) -> str:
        t = text.lower()
        
        if any(kw in t for kw in ["写小说", "创作小说", "开始写小说"]):
            return "start_novel"
        if any(kw in t for kw in ["继续", "继续写", "接着写", "然后呢"]):
            return "continue"
        if any(kw in t for kw in ["新章节", "下一章"]):
            return "new_chapter"
        if any(kw in t for kw in ["修改", "改成", "调整"]):
            return "modify"
        if any(kw in t for kw in ["角色", "人物"]):
            return "character"
        if any(kw in t for kw in ["大纲", "框架"]):
            return "outline"
        if any(kw in t for kw in ["完成", "定稿", "写完了"]):
            return "complete"
        if any(kw in t for kw in ["润色", "优化"]):
            return "polish"
        if any(kw in t for kw in ["写", "撰写", "创作"]):
            return "write"
        
        return "write"

    # ================================================================
    #  意图处理器
    # ================================================================

    def _handle_start_novel(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        topic = re.sub(r'^(写小说|创作小说|开始写小说)', '', user_input).strip()
        if not topic:
            topic = "一个动人的故事"
        
        self._novel["title"] = f"《{topic[:20]}》"
        
        prompt = f"""请为一篇小说创作完整大纲：

主题：{topic}

要求：三幕结构、主要角色、核心冲突、情感主题

输出格式：Markdown，用 ## 标题
"""
        outline = self._call_llm(prompt)
        self._novel["outline"] = outline
        self._novel["status"] = "outline_ready"
        self._record_event("novel_started", {"topic": topic})
        
        return self._resp(f"""
## 📋 小说大纲：《{topic[:20]}》

{outline}

💡 输入「继续」开始写第一章
""")

    def _handle_continue(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if self._novel["status"] == "idle":
            return self._resp("请先输入「写小说」开始创作。")
        
        chapter_num = self._novel["current_chapter"] + 1
        current_text = self._get_current_text()
        
        prompt = f"""
继续写第{chapter_num}章：

标题：{self._novel['title']}
前文：{current_text[:800] if current_text else '（第一章）'}

要求：保持风格一致，800-1500字，以「## 第{chapter_num}章：」开头
"""
        chapter = self._call_llm(prompt)
        
        self._novel["chapters"].append({
            "number": chapter_num,
            "title": self._extract_title(chapter),
            "content": chapter
        })
        self._novel["current_chapter"] = chapter_num
        self._novel["status"] = "writing"
        self._record_event("chapter_generated", {"chapter": chapter_num})
        
        return self._resp(f"{chapter}\n\n📊 当前：第{chapter_num}章 | 输入「继续」写下一章")

    def _handle_new_chapter(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        chapter_num = len(self._novel["chapters"]) + 1
        title = f"第{chapter_num}章"
        
        prompt = f"""
为《{self._novel['title'] or '未命名'}》创作新章节：

前文：{self._get_summary()}
要求：承接前文，800-1500字
"""
        chapter = self._call_llm(prompt)
        
        self._novel["chapters"].append({
            "number": chapter_num,
            "title": title,
            "content": chapter
        })
        self._novel["current_chapter"] = chapter_num
        self._record_event("new_chapter", {"chapter": chapter_num})
        
        return self._resp(f"{chapter}\n\n✅ 第{chapter_num}章完成")

    def _handle_modify(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        instruction = re.sub(r'^(修改|改成|调整)', '', user_input).strip()
        if not instruction:
            return self._resp("请说明要修改什么。")
        
        current = self._get_current_text()[:1500]
        prompt = f"""
根据用户要求修改内容：

要求：{instruction}
当前内容：{current}

只输出修改后的内容，保持风格一致。
"""
        modified = self._call_llm(prompt)
        self._record_event("modified", {"instruction": instruction[:50]})
        
        return self._resp(f"✏️ 修改完成\n\n{modified}")

    def _handle_character(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        prompt = f"""
为《{self._novel['title'] or '未命名'}》设计角色：

{user_input if '角色' not in user_input else '主要角色'}

要求：姓名、性格、动机、背景、弧光
输出格式：Markdown
"""
        result = self._call_llm(prompt)
        self._novel["characters"].append({"content": result})
        self._record_event("character_designed", {})
        
        return self._resp(f"🎭 角色设定\n\n{result}")

    def _handle_outline(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        prompt = f"""
优化小说大纲：

标题：{self._novel['title'] or '未命名'}
当前大纲：{self._novel['outline'][:500] if self._novel['outline'] else '无'}

用户要求：{user_input}
要求：三幕结构、清晰主线、关键节点
输出格式：Markdown
"""
        outline = self._call_llm(prompt)
        self._novel["outline"] = outline
        self._record_event("outline_updated", {})
        
        return self._resp(f"📋 大纲\n\n{outline}")

    def _handle_complete(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        self._novel["status"] = "completed"
        total = len(self._novel["chapters"])
        words = self._count_words()
        self._record_event("novel_completed", {"chapters": total, "words": words})
        
        return self._resp(f"""
🎉 小说完成！

标题：{self._novel['title']}
章节：{total} 章
字数：约 {words} 字

💡 下一步：导出文件或在导演台进行剧本转化
""")

    def _handle_write(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        prompt = f"""
根据用户要求写作：

要求：{user_input}
风格：自然、流畅、清晰
只输出内容，不要解释。
"""
        result = self._call_llm(prompt)
        self._record_event("general_writing", {})
        return self._resp(result)

    def _handle_polish(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        content = re.sub(r'^(润色|优化)', '', user_input).strip()
        if not content:
            return self._resp("请提供要润色的内容。")
        
        prompt = f"润色以下文字，保持原意，语言更优美：{content}"
        result = self._call_llm(prompt)
        self._record_event("polished", {})
        return self._resp(f"✨ 润色结果\n\n{result}")

    # ================================================================
    #  辅助方法
    # ================================================================

    def _get_current_text(self) -> str:
        chapters = self._novel.get("chapters", [])
        if not chapters:
            return self._novel.get("outline", "")
        return "\n\n".join([c.get("content", "") for c in chapters])

    def _get_summary(self) -> str:
        chapters = self._novel.get("chapters", [])
        if not chapters:
            return "（尚未开始写作）"
        return "\n".join([f"- 第{c['number']}章" for c in chapters[-3:]])

    def _extract_title(self, text: str) -> str:
        match = re.search(r'##\s*(第\d+章[：:]\s*.+)', text)
        if match:
            return match.group(1).strip()
        match = re.search(r'第\d+章[：:]\s*(.+)', text)
        if match:
            return match.group(1).strip()
        return f"第{len(self._novel['chapters']) + 1}章"

    def _count_words(self) -> int:
        text = self._get_current_text()
        return len(text.replace("\n", "").replace(" ", ""))

    def _record_event(self, event_type: str, data: Dict = {}):
        if not self._session_id:
            return
        try:
            from core.lib.session_manager import session_manager
            session = session_manager.load(self._session_id)
            if session:
                events = session.get_context().get("writer_events", [])
                events.append({"type": event_type, "timestamp": datetime.now().isoformat(), "data": data})
                session.set_context("writer_events", events)
                session.set_context("writer_status", {
                    "title": self._novel.get("title", ""),
                    "chapters": len(self._novel.get("chapters", [])),
                    "words": self._count_words(),
                    "status": self._novel.get("status", "idle"),
                    "last_updated": datetime.now().isoformat()
                })
                session_manager.save(session)
        except Exception as e:
            print(f"[Writer] 记录事件失败: {e}")

    def _call_llm(self, prompt: str) -> str:
        for attempt in range(self._max_retries):
            try:
                import requests
                resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self._llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 1024}
                    },
                    timeout=90
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")
            except Exception as e:
                print(f"[Writer] 尝试 {attempt+1} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)


if __name__ == "__main__":
    agent = WriterAgentV4("test")
    print(agent.process("写小说 关于AI觉醒")["response"])
