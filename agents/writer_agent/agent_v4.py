#!/usr/bin/env python3
"""WriterAgent v5.0 - 智慧型写作伙伴（完整作品）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any

from core.agents.business.business_agent import BusinessAgent


class WriterAgentV4(BusinessAgent):
    """
    写作伙伴 - 智慧型完整设计
    
    能力矩阵：
    1. 灵感孵化 → 从创意到完整大纲
    2. 角色工坊 → 深度角色设计（姓名、性格、动机、背景、弧光、关系）
    3. 章节创作 → 保持风格一致，推进情节
    4. 情节编织 → 多线叙事、转折点、情感高潮
    5. 对白打磨 → 符合角色身份的自然对白
    6. 场景构建 → 视觉化场景描述
    7. 风格迁移 → 模仿特定作家风格
    8. 一致性检查 → 角色/情节/时间线一致性
    9. 智能润色 → 保持原意的语言优化
    10. 完成定稿 → 统计、总结、导出准备
    """

    name = "writer_agent_v4"
    description = "智慧型写作伙伴"
    version = "5.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        
        # ========== 会话 ==========
        self._session_id = None
        
        # ========== 创作状态（完整） ==========
        self._novel = {
            "title": "",
            "genre": "",
            "theme": "",
            "outline": "",
            "characters": [],       # 每个角色：{name, personality, motivation, background, arc, relationships}
            "chapters": [],         # 每个章节：{number, title, content, summary}
            "scenes": [],           # 每个场景：{location, time, characters, event, emotion}
            "hooks": [],            # 伏笔/悬念：{description, chapter, resolved}
            "plot_points": [],      # 情节节点：{description, chapter, type}
            "current_chapter": 0,
            "status": "idle",       # idle | outlining | writing | revising | completed
            "word_count": 0,
            "created_at": None,
            "updated_at": None
        }
        
        # ========== 用户偏好（学习） ==========
        self._user_preferences = {
            "writing_style": "默认",      # 正式/轻松/诗意/简洁
            "preferred_genre": "通用",
            "character_depth": "详细",
            "chapter_length": "medium",   # short/medium/long
            "auto_save": True,
        }
        
        # ========== 积木（乐高集成） ==========
        self._soul = None
        self._memory = None
        self._emotion = None
        self._semantic = None
        self._proactive = None
        
        # ========== LLM 配置 ==========
        self._llm_model = "qwen2.5:7b"
        self._max_retries = 2
        
        # ========== 启动 ==========
        self._load_state()
        print(f"✍️ WriterAgent v{self.version} 已启动，我是你的写作伙伴。")
        print(f"   📖 当前状态: {self._novel['status']}")
        print(f"   📚 已写 {len(self._novel['chapters'])} 章")

    # ================================================================
    #  积木（懒加载）
    # ================================================================

    @property
    def soul(self):
        if self._soul is None:
            try:
                from core.lib.soul.soul_injector import SoulInjector
                self._soul = SoulInjector(self.user_id, "writer_agent")
            except Exception as e:
                print(f"[Writer] 加载灵魂注入器失败: {e}")
        return self._soul

    @property
    def memory(self):
        if self._memory is None:
            try:
                from core.lib.memory_layers import MemoryLayers
                self._memory = MemoryLayers()
            except Exception as e:
                print(f"[Writer] 加载记忆系统失败: {e}")
        return self._memory

    @property
    def emotion(self):
        if self._emotion is None:
            try:
                from engine.emotion import emotion_engine
                self._emotion = emotion_engine
            except Exception as e:
                print(f"[Writer] 加载情感引擎失败: {e}")
        return self._emotion

    @property
    def semantic(self):
        if self._semantic is None:
            try:
                from engine.semantic import semantic_engine
                self._semantic = semantic_engine
            except Exception as e:
                print(f"[Writer] 加载语义引擎失败: {e}")
        return self._semantic

    @property
    def proactive(self):
        if self._proactive is None:
            try:
                from core.lib.proactive_service import proactive_service
                self._proactive = proactive_service
            except Exception as e:
                print(f"[Writer] 加载主动服务失败: {e}")
        return self._proactive

    # ================================================================
    #  状态持久化
    # ================================================================

    def _load_state(self):
        """从 memory 恢复创作状态"""
        if not self._session_id:
            return
        
        try:
            if self.memory:
                state = self.memory.get_session_memory(self._session_id, limit=1)
                if state and state[0].get("novel_state"):
                    self._novel = state[0]["novel_state"]
        except Exception as e:
            print(f"[Writer] 加载状态失败: {e}")

    def _save_state(self):
        """保存创作状态到 memory"""
        if not self._session_id:
            return
        
        self._novel["updated_at"] = datetime.now().isoformat()
        self._novel["word_count"] = self._count_words()
        
        try:
            if self.memory:
                self.memory.add_session_memory(
                    self._session_id,
                    "writer_state",
                    {"novel_state": self._novel}
                )
        except Exception as e:
            print(f"[Writer] 保存状态失败: {e}")

    # ================================================================
    #  入口
    # ================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
            self._load_state()
        
        return super().process(user_input, context)

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    # ================================================================
    #  核心逻辑：感知 → 理解 → 决策 → 执行 → 学习
    # ================================================================

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        original = user_input
        
        # ========== 1. 感知层 ==========
        # 情感感知
        emotion_result = {}
        if self.emotion:
            try:
                emotion_result = self.emotion.analyze(user_input)
            except Exception as e:
                print(f"[Writer] 情感分析失败: {e}")
        
        # 语义理解
        semantic_result = None
        if self.semantic:
            try:
                semantic_result = self.semantic.understand(user_input)
            except Exception as e:
                print(f"[Writer] 语义理解失败: {e}")
        
        # 灵魂注入
        soul_context = {}
        if self.soul:
            try:
                soul_context = self.soul.inject(user_input)
            except Exception as e:
                print(f"[Writer] 灵魂注入失败: {e}")

        # ========== 2. 理解层（LLM 意图理解） ==========
        intent = self._understand_intent(user_input, semantic_result, emotion_result)
        print(f"[Writer] 意图: {intent}")

        # ========== 3. 决策与执行 ==========
        handlers = {
            "start_novel": self._handle_start_novel,
            "continue": self._handle_continue,
            "new_chapter": self._handle_new_chapter,
            "character": self._handle_character,
            "scene": self._handle_scene,
            "plot": self._handle_plot,
            "hook": self._handle_hook,
            "dialogue": self._handle_dialogue,
            "polish": self._handle_polish,
            "style": self._handle_style,
            "modify": self._handle_modify,
            "outline": self._handle_outline,
            "complete": self._handle_complete,
            "write": self._handle_write,
        }
        
        handler = handlers.get(intent, self._handle_write)
        result = handler(user_input, semantic_result, emotion_result, soul_context)
        
        # ========== 4. 学习层 ==========
        self._learn(user_input, result, intent)
        self._save_state()
        
        # ========== 5. 响应 ==========
        return self._resp(result)

    # ================================================================
    #  意图理解（LLM 驱动）
    # ================================================================

    def _understand_intent(self, user_input: str, semantic: Any, emotion: Dict) -> str:
        """由 LLM 理解意图，关键词降级"""
        text = user_input.lower()
        
        # 快速匹配（稳定降级）
        if any(kw in text for kw in ["写小说", "创作小说", "开始写小说", "新小说"]):
            return "start_novel"
        if any(kw in text for kw in ["继续", "继续写", "接着写", "然后呢", "再写"]):
            return "continue"
        if any(kw in text for kw in ["新章节", "下一章", "开始新的一章"]):
            return "new_chapter"
        if any(kw in text for kw in ["角色", "人物", "主角", "配角"]):
            return "character"
        if any(kw in text for kw in ["场景", "环境", "背景"]):
            return "scene"
        if any(kw in text for kw in ["情节", "剧情", "转折", "冲突"]):
            return "plot"
        if any(kw in text for kw in ["钩子", "悬念", "伏笔"]):
            return "hook"
        if any(kw in text for kw in ["对白", "对话", "台词"]):
            return "dialogue"
        if any(kw in text for kw in ["润色", "优化", "美化"]):
            return "polish"
        if any(kw in text for kw in ["风格", "模仿", "像"]):
            return "style"
        if any(kw in text for kw in ["修改", "改成", "调整"]):
            return "modify"
        if any(kw in text for kw in ["大纲", "框架", "结构"]):
            return "outline"
        if any(kw in text for kw in ["完成", "定稿", "写完了"]):
            return "complete"
        
        # 默认写作
        return "write"

    # ================================================================
    #  意图处理器（完整能力矩阵）
    # ================================================================

    def _handle_start_novel(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """① 灵感孵化 → 完整大纲"""
        # 提取主题
        topic = re.sub(r'^(写小说|创作小说|开始写小说|新小说)', '', user_input).strip()
        if not topic:
            topic = "一个动人的故事"
        
        # 检测体裁
        genre = "通用"
        for g in ["科幻", "奇幻", "悬疑", "爱情", "动作", "喜剧", "悲剧", "史诗"]:
            if g in user_input:
                genre = g
                break
        
        self._novel["title"] = f"《{topic[:20]}》"
        self._novel["genre"] = genre
        self._novel["theme"] = topic
        self._novel["status"] = "outlining"
        
        prompt = f"""
请为一篇小说创作完整大纲：

主题：{topic}
体裁：{genre}

要求：
1. 三幕结构（开端-发展-高潮-结局）
2. 主要角色（至少2个，含姓名、性格、动机）
3. 核心冲突
4. 故事主线
5. 情感主题
6. 预计章节数

输出格式：Markdown
"""
        outline = self._call_llm(prompt)
        self._novel["outline"] = outline
        self._novel["status"] = "outlining"
        self._novel["created_at"] = datetime.now().isoformat()
        self._save_state()
        
        return f"""
## 📋 小说大纲：《{topic[:20]}》

**体裁**：{genre}

{outline}

---

💡 **下一步建议：**
- 输入「继续写第一章」开始创作
- 输入「角色」设计角色细节
- 输入「修改大纲」调整框架

> 有任何问题随时告诉我，我们是在一起创作。
"""

    def _handle_continue(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """② 继续创作（感知上下文，保持风格）"""
        if self._novel["status"] == "idle":
            return "请先输入「写小说」开始创作。"
        
        chapter_num = self._novel["current_chapter"] + 1
        current_text = self._get_current_text()
        
        # 检测是否有用户方向指示
        direction = ""
        if "写" in user_input and len(user_input) > 5:
            direction = f"用户希望：{user_input}"
        
        prompt = f"""
继续写第{chapter_num}章：

小说：{self._novel['title']}
体裁：{self._novel['genre']}
前文：{current_text[:800] if current_text else '（这是第一章）'}

{direction}

要求：
1. 保持前文的风格和语气
2. 推进情节发展
3. 本章应有完整的起承转合
4. 字数：800-1500字
5. 以「## 第{chapter_num}章：」开头
"""
        chapter = self._call_llm(prompt)
        
        self._novel["chapters"].append({
            "number": chapter_num,
            "title": self._extract_title(chapter),
            "content": chapter,
            "summary": self._extract_summary(chapter),
            "created_at": datetime.now().isoformat()
        })
        self._novel["current_chapter"] = chapter_num
        self._novel["status"] = "writing"
        self._update_stats()  # ← 加上
        self._save_state()
        
        return f"""
{chapter}

---

📊 **进度更新**
- 当前章节：第{chapter_num}章
- 总字数：约 {self._count_words()} 字
- 输入「继续」写下一章
- 输入「修改」调整本章内容

> 写得不错，继续保持。
"""

    def _handle_new_chapter(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """③ 新建章节（用户指定标题）"""
        chapter_num = len(self._novel["chapters"]) + 1
        
        # 提取用户指定的标题
        title = re.sub(r'^(新章节|下一章)', '', user_input).strip()
        if not title:
            title = f"第{chapter_num}章"
        
        prompt = f"""
为小说《{self._novel['title'] or '未命名'}》创作新章节：

章节标题：{title}
前文概要：{self._get_summary()}

要求：
1. 自然承接前文
2. 推动故事发展
3. 800-1500字
"""
        chapter = self._call_llm(prompt)
        
        self._novel["chapters"].append({
            "number": chapter_num,
            "title": title,
            "content": chapter,
            "summary": self._extract_summary(chapter),
            "created_at": datetime.now().isoformat()
        })
        self._novel["current_chapter"] = chapter_num
        self._novel["status"] = "writing"
        self._save_state()
        
        return f"""
{chapter}

---

✅ 第{chapter_num}章「{title}」已生成
📊 总字数：约 {self._count_words()} 字
"""

    def _handle_character(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """④ 角色工坊（深度角色设计）"""
        # 提取角色名
        name_match = re.search(r'角色\s*([^\s，,。.]+)', user_input)
        character_name = name_match.group(1) if name_match else None
        
        prompt = f"""
为小说《{self._novel['title'] or '未命名'}》设计角色：

{user_input if '角色' not in user_input else '主要角色'}

要求：
1. 姓名、年龄、外貌特征
2. 性格特点（优点、缺点、习惯、口头禅）
3. 核心动机（想要什么、为什么）
4. 背景故事（关键经历）
5. 角色弧光（如何成长和变化）
6. 与其他角色的关系
7. 在故事中的作用

输出格式：Markdown
"""
        result = self._call_llm(prompt)
        
        # 存储角色信息
        if character_name:
            self._novel["characters"].append({
                "name": character_name,
                "profile": result,
                "created_at": datetime.now().isoformat()
            })
        else:
            self._novel["characters"].append({
                "profile": result,
                "created_at": datetime.now().isoformat()
            })
        self._update_stats()  # ← 加上
        self._save_state()
        
        return f"""
🎭 角色设定

{result}

---

💡 这个角色可以更立体吗？输入「继续深化」或告诉我想调整什么。
"""

    def _handle_scene(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑤ 场景构建"""
        prompt = f"""
为小说《{self._novel['title'] or '未命名'}》构建场景：

用户要求：{user_input}

要求：
1. 地点和时间
2. 场景氛围（通过光线、声音、温度、气味营造）
3. 在场角色
4. 主要事件
5. 场景在故事中的作用

输出格式：Markdown
"""
        result = self._call_llm(prompt)
        self._novel["scenes"].append({
            "content": result,
            "created_at": datetime.now().isoformat()
        })
        self._update_stats()  # ← 加上
        self._save_state()
        
        return f"""
🏗️ 场景构建

{result}

---

💡 这个场景的细节还可以更丰富。
"""

    def _handle_plot(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑥ 情节编织"""
        prompt = f"""
为小说《{self._novel['title'] or '未命名'}》设计情节节点：

用户要求：{user_input}

要求：
1. 主要冲突（人与人/人与环境/人与自我）
2. 关键转折点
3. 情感高潮
4. 结局走向
5. 多线交织（如有）

输出格式：Markdown
"""
        result = self._call_llm(prompt)
        self._novel["plot_points"].append({
            "content": result,
            "created_at": datetime.now().isoformat()
        })
        self._update_stats()  # ← 加上
        self._save_state()
        
        return f"""
🎯 情节设计

{result}

---

💡 情节的张力还可以再强一些。
"""

    def _handle_hook(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑦ 钩子设计（悬念/伏笔）"""
        prompt = f"""
为小说《{self._novel['title'] or '未命名'}》设计钩子（悬念/伏笔）：

用户要求：{user_input}

要求：
1. 吸引力强
2. 与主线相关
3. 可回收
4. 类型：悬念/伏笔/转折/揭秘
5. 建议埋设章节

输出格式：Markdown
"""
        result = self._call_llm(prompt)
        self._novel["hooks"].append({
            "content": result,
            "created_at": datetime.now().isoformat()
        })
        self._update_stats()  # ← 加上
        self._save_state()
        
        return f"""
🪝 钩子设计

{result}

---

💡 好的钩子能让读者放不下书。
"""

    def _handle_dialogue(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑧ 对白打磨"""
        prompt = f"""
根据用户要求生成或优化对白：

用户要求：{user_input}
小说体裁：{self._novel['genre']}

要求：
1. 符合角色身份和性格
2. 推动情节发展
3. 自然、有节奏
4. 潜台词（话里有话）

输出格式：标准剧本对白格式
"""
        result = self._call_llm(prompt)
        return f"""
🎙️ 对白设计

{result}

---

💡 对白的节奏和潜台词还可以再打磨。
"""

    def _handle_polish(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑨ 智能润色"""
        content = re.sub(r'^(润色|优化)', '', user_input).strip()
        if not content:
            return "请提供要润色的内容。"
        
        prompt = f"""
润色以下文字：

原文：{content}

要求：
1. 保持原意
2. 语言更优美
3. 更符合{self._user_preferences.get('writing_style', '默认')}风格
4. 只输出润色后的结果
"""
        result = self._call_llm(prompt)
        return f"""
✨ 润色结果

{result}
"""

    def _handle_style(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑩ 风格迁移"""
        style_match = re.search(r'模仿\s*([^\s，,。.]+)\s*风格', user_input)
        if style_match:
            style = style_match.group(1)
            self._user_preferences["writing_style"] = style
            self._save_state()
            return f"✅ 已切换写作风格：{style}"
        
        return """
🎨 风格迁移

支持风格：
- 海明威（简洁、硬朗）
- 张爱玲（细腻、冷峻）
- 村上春树（孤独、轻盈）
- 鲁迅（深刻、犀利）
- 金庸（豪迈、古典）

示例：模仿 海明威 风格写一段
"""

    def _handle_modify(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        instruction = re.sub(r'^(修改|改成|调整)', '', user_input).strip()
        if not instruction:
            return "请说明要修改什么。"
    
        # 检查是否是角色修改
        name_match = re.search(r'([^\s，,。.]+)\s*改成\s*([^\s，,。.]+)', instruction)
        if name_match:
            old_name, new_name = name_match.group(1), name_match.group(2)
            for char in self._novel["characters"]:
                if char.get("name") == old_name:
                    char["name"] = new_name
                    self._save_state()
                    return f"✅ 已将角色名从「{old_name}」改为「{new_name}」"
            return f"❌ 未找到角色「{old_name}」"
    
        # 通用修改
        current = self._get_current_text()[:1500]
        prompt = f"""
根据用户要求修改内容：

要求：{instruction}
当前内容：{current}

要求：
1. 精准修改
2. 保持整体结构不变
3. 只输出修改后的内容
"""
        modified = self._call_llm(prompt)
        return f"✏️ 修改完成\n\n{modified}"

    def _handle_outline(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑫ 大纲优化"""
        prompt = f"""
优化小说大纲：

标题：{self._novel['title'] or '未命名'}
当前大纲：{self._novel['outline'][:500] if self._novel['outline'] else '无'}

用户要求：{user_input}

要求：
1. 三幕结构清晰
2. 主线明确
3. 关键节点突出
4. 节奏合理

输出格式：Markdown
"""
        outline = self._call_llm(prompt)
        self._novel["outline"] = outline
        self._save_state()
        
        return f"""
📋 大纲已更新

{outline}
"""

   
    def _handle_complete(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        total = len(self._novel["chapters"])
        words = self._count_words()
    
        # 完成判断
        if total < 3:
            return f"""
📝 目前只写了 {total} 章（约 {words} 字），还不够完整。

💡 建议：
- 继续写直到至少 3 章
- 或者告诉我「强制完成」
- 真正的作品值得完整呈现

> 不急，好作品需要时间。
"""
    
        self._novel["status"] = "completed"
        self._save_state()
    
        return f"""
🎉 小说完成！

标题：{self._novel['title']}
体裁：{self._novel['genre']}
章节：{total} 章
字数：约 {words} 字

📊 **统计**
- 角色：{len(self._novel['characters'])} 个
- 场景：{len(self._novel['scenes'])} 个
- 情节节点：{len(self._novel['plot_points'])} 个
- 钩子：{len(self._novel['hooks'])} 个

💡 **下一步：**
- 在导演台导入进行剧本转化
- 导出保存为文件
- 继续「修改」完善细节

> 你完成了一部作品，值得骄傲。
"""

    def _handle_write(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """⑭ 通用写作"""
        prompt = f"""
根据用户要求写作：

要求：{user_input}
风格：{self._user_preferences.get('writing_style', '默认')}

要求：
1. 语言流畅、自然
2. 表达清晰
3. 只输出内容，不要解释
"""
        result = self._call_llm(prompt)
        return result

    # ================================================================
    #  学习层
    # ================================================================

    def _learn(self, user_input: str, result: str, intent: str):
        """从交互中学习"""
        # 检测用户偏好
        if "风格" in user_input.lower() and "模仿" in user_input.lower():
            style_match = re.search(r'模仿\s*([^\s，,。.]+)', user_input)
            if style_match:
                self._user_preferences["writing_style"] = style_match.group(1)
        
        # 检测体裁偏好
        for g in ["科幻", "奇幻", "悬疑", "爱情", "动作", "喜剧"]:
            if g in user_input:
                self._user_preferences["preferred_genre"] = g
        
        # 记录学习事件
        if self.soul:
            try:
                self.soul.update_relationship(user_input, result)
            except Exception as e:
                print(f"[Writer] 学习失败: {e}")

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
        return "\n".join([f"- 第{c['number']}章：{c.get('title', '')}" for c in chapters[-3:]])

    def _extract_title(self, text: str) -> str:
        match = re.search(r'##\s*(第\d+章[：:]\s*.+)', text)
        if match:
            return match.group(1).strip()
        match = re.search(r'第\d+章[：:]\s*(.+)', text)
        if match:
            return match.group(1).strip()
        return f"第{len(self._novel['chapters']) + 1}章"

    def _extract_summary(self, text: str) -> str:
        """提取章节摘要"""
        lines = text.split('\n')
        if len(lines) > 3:
            return ' '.join(lines[:3])[:100] + '...'
        return text[:100]

    def _count_words(self) -> int:
        text = self._get_current_text()
        return len(text.replace("\n", "").replace(" ", ""))

    # 不同任务使用不同的输出长度
    def _get_llm_config(self, task_type: str) -> Dict:
        """根据任务类型返回不同的 LLM 配置"""
        configs = {
            "outline": {"num_predict": 4096},      # 大纲需要 3000+ 字
            "chapter": {"num_predict": 2048},      # 章节 1500-2000 字
            "character": {"num_predict": 2048},    # 角色设计 1500+ 字
            "polish": {"num_predict": 1024},       # 润色 500-800 字
            "default": {"num_predict": 2048},
        }
        return configs.get(task_type, configs["default"])

    def _call_llm(self, prompt: str, task_type: str = "default") -> str:
        config = self._get_llm_config(task_type)
    
        for attempt in range(self._max_retries):
            try:
                import requests
                resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self._llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": config["num_predict"],  # 任务相关
                            "top_p": 0.9,
                        }
                    },
                    timeout=120  # 增加超时时间
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")
            except Exception as e:
                print(f"[Writer] 尝试 {attempt+1} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def _update_stats(self):
        """更新统计信息"""
        self._novel["word_count"] = self._count_words()
        self._novel["updated_at"] = datetime.now().isoformat()
        self._save_state()


if __name__ == "__main__":
    agent = WriterAgentV4("test")
    print("=" * 50)
    print("WriterAgent 完整测试")
    print("=" * 50)
    
    result = agent.process("写小说 关于AI觉醒", {"session_id": "test_session"})
    print(result.get("response"))
