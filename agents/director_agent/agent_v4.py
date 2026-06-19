#!/usr/bin/env python3
"""DirectorAgent v5.0 - 智慧型电影制作导演（完整作品）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass, field, asdict

from core.agents.business.business_agent import BusinessAgent


@dataclass
class FilmProject:
    """电影项目 - 完整状态"""
    id: str
    title: str
    genre: str
    status: str  # concept | pre_production | production | post_production | released
    progress: int
    script: str = ""
    script_summary: str = ""  # 剧本摘要
    characters: List[Dict] = field(default_factory=list)  # {name, role, profile, arc}
    scenes: List[Dict] = field(default_factory=list)  # {location, time, event, emotion, characters}
    plot_points: List[Dict] = field(default_factory=list)  # {type, description, chapter}
    budget: float = 0.0
    timeline: Dict = field(default_factory=dict)  # {pre_production: "", production: "", post_production: ""}
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1


class DirectorAgentV4(BusinessAgent):
    """
    导演 Agent - 智慧型完整设计

    能力矩阵：
    1. 项目孵化 → 从创意到完整项目框架
    2. 剧本创作 → 标准剧本格式（含三幕结构）
    3. 角色工坊 → 深度角色设计 + 关系网
    4. 场景设计 → 场景列表 + 冲突密度分析
    5. 质量审查 → 5 维度评分 + 改进建议
    6. 迭代精炼 → 基于反馈精准修改
    7. 项目报告 → 完整数据汇总
    8. 发布管理 → 项目完成 & 归档
    """

    name = "director_agent_v4"
    description = "智慧型电影制作导演"
    version = "5.0.0"

    GENRES = ["动作", "喜剧", "剧情", "科幻", "奇幻", "悬疑", "爱情", "动画", "纪录片", "恐怖", "冒险"]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

        # ========== 会话 ==========
        self._session_id = None

        # ========== 项目状态 ==========
        self._project: Optional[FilmProject] = None

        # ========== 积木（乐高集成） ==========
        self._soul = None
        self._memory = None
        self._semantic = None

        # ========== LLM 配置（任务自适应） ==========
        self._llm_model = "qwen2.5:7b"
        self._max_retries = 2
        self._llm_configs = {
            "script": {"num_predict": 4096, "temperature": 0.7},    # 剧本需要长输出
            "review": {"num_predict": 2048, "temperature": 0.3},    # 审查需要稳定
            "character": {"num_predict": 2048, "temperature": 0.7},
            "scene": {"num_predict": 2048, "temperature": 0.7},
            "refine": {"num_predict": 2048, "temperature": 0.5},
            "default": {"num_predict": 2048, "temperature": 0.7},
        }

        print(f"🎬 DirectorAgent v{self.version} 已启动，我是你的电影制作伙伴。")

    # ================================================================
    #  积木（懒加载）
    # ================================================================

    @property
    def soul(self):
        if self._soul is None:
            try:
                from core.lib.soul.soul_injector import SoulInjector
                self._soul = SoulInjector(self.user_id, "director_agent")
            except Exception as e:
                print(f"[Director] 加载灵魂注入器失败: {e}")
        return self._soul

    @property
    def memory(self):
        if self._memory is None:
            try:
                from core.lib.memory_layers import MemoryLayers
                self._memory = MemoryLayers()
            except Exception as e:
                print(f"[Director] 加载记忆系统失败: {e}")
        return self._memory

    @property
    def semantic(self):
        if self._semantic is None:
            try:
                from engine.semantic import semantic_engine
                self._semantic = semantic_engine
            except Exception as e:
                print(f"[Director] 加载语义引擎失败: {e}")
        return self._semantic

    # ================================================================
    #  入口
    # ================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
            self._load_project_from_session()
        return super().process(user_input, context)

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    # ================================================================
    #  核心逻辑：感知 → 理解 → 决策 → 执行 → 学习
    # ================================================================

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        original = user_input
        t = user_input.lower()

        # ========== 感知层 ==========
        semantic_result = None
        if self.semantic:
            try:
                semantic_result = self.semantic.understand(user_input)
            except Exception as e:
                print(f"[Director] 语义理解失败: {e}")

        soul_context = {}
        if self.soul:
            try:
                soul_context = self.soul.inject(user_input)
            except Exception as e:
                print(f"[Director] 灵魂注入失败: {e}")

        # ========== 意图检测 ==========
        intent = self._detect_intent(user_input)
        print(f"[Director] 意图: {intent}")

        # ========== 执行 ==========
        handlers = {
            "create": self._handle_create,
            "script": self._handle_script,
            "characters": self._handle_characters,
            "scenes": self._handle_scenes,
            "review": self._handle_review,
            "refine": self._handle_refine,
            "export": self._handle_export,
            "status": self._handle_status,
            "report": self._handle_report,
            "release": self._handle_release,
        }

        handler = handlers.get(intent, self._handle_help)
        result = handler(user_input, semantic_result, soul_context)

        # ========== 学习 ==========
        if self.soul and self._project:
            try:
                self.soul.update_relationship(original, result)
            except Exception as e:
                print(f"[Director] 学习失败: {e}")

        return self._resp(result)

    # ================================================================
    #  意图检测
    # ================================================================

    def _detect_intent(self, user_input: str) -> str:
        t = user_input.lower()

        if any(kw in t for kw in ["创建", "新项目", "拍电影", "制作电影", "创作"]):
            return "create"
        if any(kw in t for kw in ["写剧本", "剧本"]):
            return "script"
        if any(kw in t for kw in ["角色", "人物"]):
            return "characters"
        if any(kw in t for kw in ["场景", "分镜"]):
            return "scenes"
        if any(kw in t for kw in ["审查", "质量", "评价", "评分"]):
            return "review"
        if any(kw in t for kw in ["精炼", "优化", "修改", "改进"]):
            return "refine"
        if any(kw in t for kw in ["导出", "export"]):
            return "export"
        if any(kw in t for kw in ["状态", "进度"]):
            return "status"
        if any(kw in t for kw in ["报告", "统计"]):
            return "report"
        if any(kw in t for kw in ["发布", "上映", "完成"]):
            return "release"

        return "help"

    # ================================================================
    #  ① 项目孵化
    # ================================================================

    def _handle_create(self, user_input: str, semantic: Any, soul: Dict) -> str:
        title = self._extract_title(user_input)
        genre = self._detect_genre(user_input)

        self._project = FilmProject(
            id=f"film_{int(time.time())}",
            title=title,
            genre=genre,
            status="concept",
            progress=0
        )

        # 生成项目摘要
        prompt = f"""
为电影《{title}》生成一个简短的项目描述（50字以内）：

类型：{genre}
这个故事的核心理念是什么？
"""
        summary = self._call_llm(prompt, "default")
        if summary:
            self._project.script_summary = summary.strip()

        self._save_project_to_session()

        return f"""
## 🎬 项目创建成功

**标题**：{title}
**类型**：{genre}
**状态**：概念开发
**进度**：0%

📝 **项目简介**：
{self._project.script_summary or "一部精彩的{genre}电影"}

---

💡 **下一步建议**：
- 输入「写剧本」开始创作
- 输入「角色」设计角色
- 输入「场景」设计场景

> 每个伟大的电影都从一个想法开始。
"""
        print(f"[Director] 项目已创建: {self._project.title if self._project else 'None'}")
    # ================================================================
    #  ② 剧本创作
    # ================================================================

    def _handle_script(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。输入「创建项目」开始。"

        prompt = f"""
为电影《{self._project.title}》创作完整剧本：

类型：{self._project.genre}

**要求**：
1. 三幕结构（开端-发展-高潮-结局）
2. 场景标题（INT./EXT. + 地点 + 时间）
3. 动作描述（简洁、视觉化）
4. 角色对白（角色名: 对白）
5. 角色弧光完整
6. 情感高潮
7. 结尾要有余韵

**输出格式**：标准剧本格式
**字数**：2000-4000字
"""
        script = self._call_llm(prompt, "script")

        if script:
            self._project.script = script
            self._project.progress = 25
            self._project.version += 1
            self._project.updated_at = datetime.now().isoformat()
            self._save_project_to_session()

            preview = script[:800] + "..." if len(script) > 800 else script
            return f"""
## ✍️ 剧本创作完成

📊 **进度**：25%
📝 **字数**：约 {len(script)} 字符
📌 **版本**：v{self._project.version}

### 📖 剧本预览

{preview}

---

💡 **下一步建议**：
- 输入「角色」设计角色
- 输入「场景」设计场景
- 输入「审查」评估剧本质量

> 剧本是电影的灵魂。
"""

        return "剧本生成失败，请重试。"

    # ================================================================
    #  ③ 角色工坊
    # ================================================================

    def _handle_characters(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        # 检测是否指定了角色名
        name_match = re.search(r'角色\s*([^\s，,。.]+)', user_input)
        specific_name = name_match.group(1) if name_match else None

        prompt = f"""
为电影《{self._project.title}》设计主要角色：

类型：{self._project.genre}
{self._project.script[:500] if self._project.script else ''}

要求：
1. **主角**：姓名、年龄、外貌、性格（优点+缺点）、核心动机、背景故事、角色弧光
2. **配角**（2-3个）：姓名、性格、功能
3. **反派**（如有）：姓名、动机、与主角的冲突
4. **角色关系网**：主要角色之间的关系

{"特别关注角色：" + specific_name if specific_name else ""}

输出格式：Markdown
"""
        result = self._call_llm(prompt, "character")

        if result:
            self._project.characters.append({
                "content": result,
                "generated_at": datetime.now().isoformat()
            })
            self._project.progress = max(self._project.progress, 35)
            self._save_project_to_session()

            return f"""
## 🎭 角色设定完成

📊 **进度**：{self._project.progress}%

{result}

---

💡 **下一步建议**：
- 输入「场景」设计场景
- 输入「审查」评估剧本质量

> 角色是故事的灵魂，观众通过他们感受故事。
"""

        return "角色设定失败，请重试。"

    # ================================================================
    #  ④ 场景设计
    # ================================================================

    def _handle_scenes(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        prompt = f"""
为电影《{self._project.title}》设计关键场景：

类型：{self._project.genre}
剧本摘要：{self._project.script[:500] if self._project.script else '（剧本未完成）'}

**要求**：
1. 列出 **5-8 个关键场景**
2. 每个场景包含：
   - 地点和时间
   - 主要事件
   - 参与角色
   - 情绪基调
   - 冲突密度（1-10）
3. 场景之间的逻辑连贯性
4. 标注场景类型：动作/对话/内心/转折

**输出格式**：Markdown 表格 + 描述
"""
        result = self._call_llm(prompt, "scene")

        if result:
            self._project.scenes.append({
                "content": result,
                "generated_at": datetime.now().isoformat()
            })
            self._project.progress = max(self._project.progress, 45)
            self._save_project_to_session()

            return f"""
## 🎨 场景设计完成

📊 **进度**：{self._project.progress}%

{result}

---

💡 **下一步建议**：
- 输入「审查」评估剧本质量
- 输入「发布」完成项目

> 场景是故事的骨骼，支撑起整个叙事。
"""

        return "场景设计失败，请重试。"

    # ================================================================
    #  ⑤ 质量审查
    # ================================================================

    def _handle_review(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        if not self._project.script:
            return "请先生成剧本。输入「写剧本」开始。"

        prompt = f"""
请专业审查以下剧本：

**剧本**：
{self._project.script[:4000]}

**审查维度**（1-10分）：
1. **结构完整性**：三幕结构是否清晰
2. **角色一致性**：角色言行是否统一
3. **对白质量**：是否自然流畅，推动情节
4. **节奏控制**：张弛有度，吸引观众
5. **主题表达**：核心思想是否清晰

**输出格式**：
### 📊 评分
| 维度 | 评分 | 评语 |
|------|------|------|

### 💡 改进建议
- 建议1
- 建议2

### 🎯 整体评价
一句话总结剧本质量。
"""
        review = self._call_llm(prompt, "review")

        return f"""
## 📊 剧本审查报告

**项目**：{self._project.title}
**版本**：v{self._project.version}

{review}

---

💡 **下一步建议**：
- 输入「精炼 [反馈]」修改剧本
- 输入「场景」设计场景

> 好的剧本是改出来的。
"""

    # ================================================================
    #  ⑥ 迭代精炼
    # ================================================================

    def _handle_refine(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        if not self._project.script:
            return "请先生成剧本。"

        feedback = re.sub(r'^(精炼|优化|修改|改进)', '', user_input).strip()
        if not feedback:
            return """
请说明修改意见。例如：
- 精炼 主角对话更幽默
- 优化 第三幕节奏加快
- 修改 结局更开放
"""

        prompt = f"""
根据用户反馈修改剧本：

**剧本**：
{self._project.script[:3000]}

**用户反馈**：
{feedback}

**要求**：
1. 精准修改，不改变整体结构
2. 保持风格一致
3. 只输出修改后的内容
4. 标注修改位置
"""
        refined = self._call_llm(prompt, "refine")

        if refined:
            self._project.script = refined
            self._project.version += 1
            self._project.updated_at = datetime.now().isoformat()
            self._save_project_to_session()

            return f"""
## ✅ 精炼完成

**版本**：v{self._project.version}
**修改依据**：{feedback}

📝 **修改后的内容**：
{refined[:800]}{"..." if len(refined) > 800 else ""}

---

💡 输入「审查」查看新版本质量
"""

        return "精炼失败，请重试。"

    # ================================================================
    #  ⑦ 项目报告
    # ================================================================

    def _handle_report(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "暂无项目。输入「创建项目」开始。"

        p = self._project

        return f"""
## 📊 项目报告

### 📋 基本信息
| 项目 | 内容 |
|------|------|
| 标题 | {p.title} |
| 类型 | {p.genre} |
| 状态 | {p.status} |
| 进度 | {p.progress}% |
| 版本 | v{p.version} |
| 创建时间 | {p.created_at[:19].replace('T', ' ')} |
| 更新时间 | {p.updated_at[:19].replace('T', ' ')} |

### 📝 剧本统计
- 字符数：{len(p.script)} 字符
- 预估场景数：{len(p.scenes)} 个
- 角色数：{len(p.characters)} 个

### 🎯 里程碑
- ✅ 概念开发：已完成
- {'✅' if len(p.script) > 100 else '⬜'} 剧本创作：{"已完成" if len(p.script) > 100 else "进行中"}
- {'✅' if len(p.characters) > 0 else '⬜'} 角色设定：{"已完成" if len(p.characters) > 0 else "进行中"}
- {'✅' if len(p.scenes) > 0 else '⬜'} 场景设计：{"已完成" if len(p.scenes) > 0 else "进行中"}

💡 **提示**：输入「发布」完成项目
"""

    # ================================================================
    #  ⑧ 发布
    # ================================================================

    def _handle_release(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        if not self._project.script or len(self._project.script) < 500:
            return """
⚠️ 剧本尚未完成（少于500字符），建议：
- 输入「写剧本」完成创作
- 或者输入「强制发布」强行发布
"""

        self._project.status = "released"
        self._project.progress = 100
        self._project.updated_at = datetime.now().isoformat()
        self._save_project_to_session()

        return f"""
## 🚀 项目发布完成！

🎬 **{self._project.title}** 已正式发布！

### 📊 最终统计
| 项目 | 数据 |
|------|------|
| 类型 | {self._project.genre} |
| 剧本字数 | {len(self._project.script)} 字符 |
| 角色数 | {len(self._project.characters)} 个 |
| 场景数 | {len(self._project.scenes)} 个 |
| 版本 | v{self._project.version} |

### 📝 项目摘要
{self._project.script_summary or "一部精彩的{self._project.genre}电影"}

---

🎉 恭喜完成电影制作！

💡 **下一步**：
- 输入「导出」保存剧本文件
- 输入「报告」查看完整统计
- 输入「创建项目」开始新作品

> 一部电影完成了，但故事会永远留在观众心里。
"""

    # ================================================================
    #  导出
    # ================================================================

    def _handle_export(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "请先创建项目。"

        if not self._project.script:
            return "请先生成剧本。"

        content = f"""标题：{self._project.title}
类型：{self._project.genre}
状态：{self._project.status}
进度：{self._project.progress}%
版本：v{self._project.version}
创建时间：{self._project.created_at}
更新时间：{self._project.updated_at}

{'='*60}
{self._project.script}
"""

        filename = f"/tmp/{self._project.title}_剧本.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return f"""
✅ 已导出剧本到：{filename}

📊 **文件信息**：
- 大小：{len(content)} 字符
- 格式：TXT
- 版本：v{self._project.version}

💡 支持格式：TXT、Fountain（后续支持）
"""

    # ================================================================
    #  状态/帮助
    # ================================================================

    def _handle_status(self, user_input: str, semantic: Any, soul: Dict) -> str:
        if not self._project:
            return "暂无项目。输入「创建项目」开始。"

        p = self._project
        return f"""
## 📊 项目状态

**标题**：{p.title}
**类型**：{p.genre}
**状态**：{p.status}
**进度**：{p.progress}%
**版本**：v{p.version}

### 📝 内容统计
- 剧本：{len(p.script)} 字符
- 角色：{len(p.characters)} 个
- 场景：{len(p.scenes)} 个

### ⏱️ 时间线
- 创建：{p.created_at[:19].replace('T', ' ')}
- 更新：{p.updated_at[:19].replace('T', ' ')}

💡 输入「报告」查看完整报告
"""

    def _handle_help(self, user_input: str, semantic: Any, soul: Dict) -> str:
        return """
🎬 **导演助手 - 帮助**

我是你的电影制作伙伴，帮你从创意到成片。

### 可用指令

| 指令 | 功能 |
|------|------|
| `创建项目` | 创建新电影项目 |
| `写剧本` | 创作完整剧本 |
| `角色` | 设计角色 |
| `场景` | 设计场景 |
| `审查` | 质量评估 |
| `精炼 [反馈]` | 根据反馈修改 |
| `状态` | 查看项目状态 |
| `报告` | 完整项目报告 |
| `导出` | 导出剧本文件 |
| `发布` | 完成项目 |

### 示例
创建项目 科幻电影 星际迷航
写剧本
角色 主角是位女科学家
审查
精炼 主角对话更幽默
发布

💡 开始你的电影创作之旅吧！
"""

    # ================================================================
    #  画布节点执行（兼容）
    # ================================================================

    def execute_node(self, node_type: str, params: Dict) -> Dict:
        handlers = {
            "script_generator": self._execute_script_generator,
            "character_design": self._execute_character_design,
            "scene_design": self._execute_scene_design,
            "quality_review": self._execute_quality_review,
            "export_script": self._execute_export_script,
            "project_report": self._execute_project_report,
        }

        handler = handlers.get(node_type)
        if not handler:
            return {"success": False, "error": f"未知节点: {node_type}"}

        try:
            return handler(params)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_script_generator(self, params: Dict) -> Dict:
        if not self._project:
            return {"success": False, "error": "请先创建项目"}

        prompt = f"为《{self._project.title}》创作完整剧本：类型 {self._project.genre}"
        script = self._call_llm(prompt, "script")
        if script:
            self._project.script = script
            self._project.progress = 25
            self._save_project_to_session()
            return {"success": True, "result": script}
        return {"success": False, "error": "生成失败"}

    def _execute_character_design(self, params: Dict) -> Dict:
        if not self._project:
            return {"success": False, "error": "请先创建项目"}

        prompt = f"为《{self._project.title}》设计角色"
        result = self._call_llm(prompt, "character")
        if result:
            self._project.characters.append({"content": result})
            self._project.progress = 35
            self._save_project_to_session()
            return {"success": True, "result": result}
        return {"success": False, "error": "设计失败"}

    def _execute_scene_design(self, params: Dict) -> Dict:
        if not self._project:
            return {"success": False, "error": "请先创建项目"}

        prompt = f"为《{self._project.title}》设计场景"
        result = self._call_llm(prompt, "scene")
        if result:
            self._project.scenes.append({"content": result})
            self._project.progress = 45
            self._save_project_to_session()
            return {"success": True, "result": result}
        return {"success": False, "error": "设计失败"}

    def _execute_quality_review(self, params: Dict) -> Dict:
        if not self._project or not self._project.script:
            return {"success": False, "error": "请先生成剧本"}

        prompt = f"审查剧本：{self._project.script[:2000]}"
        review = self._call_llm(prompt, "review")
        return {"success": True, "result": review or "审查完成"}

    def _execute_export_script(self, params: Dict) -> Dict:
        if not self._project or not self._project.script:
            return {"success": False, "error": "请先生成剧本"}

        filename = f"/tmp/{self._project.title}_script.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self._project.script)
        return {"success": True, "result": f"已导出: {filename}"}

    def _execute_project_report(self, params: Dict) -> Dict:
        if not self._project:
            return {"success": False, "error": "请先创建项目"}

        p = self._project
        report = f"""
标题: {p.title}
类型: {p.genre}
状态: {p.status}
进度: {p.progress}%
剧本: {len(p.script)} 字符
角色: {len(p.characters)} 个
场景: {len(p.scenes)} 个
"""
        return {"success": True, "result": report}

    # ================================================================
    #  辅助方法
    # ================================================================
   
    def _extract_title(self, text: str) -> str:
        """使用 LLM 提取电影标题"""
        prompt = f"""
从以下用户输入中提取电影标题，只输出标题本身，不要其他内容：

用户输入：{text}

要求：
- 如果没有明确的标题，输出"未命名作品"
- 只输出标题，不要有任何解释
- 不要带书名号

标题：
"""
        result = self._call_llm(prompt, "default")
        if result and len(result) < 30:
            title = result.strip()
            # 如果 LLM 返回了"未命名作品"或空，降级到正则
            if title and title != "未命名作品" and title not in ["科幻", "电影", "作品"]:
                return title
    
        # 降级：正则提取
        match = re.search(r'[《「『]\s*(.+?)\s*[》」』]', text)
        if match:
            return match.group(1)
        match = re.search(r'(?:创作|制作|拍)\s*(?:一部)?\s*(.+?)\s*(?:电影|作品|影片)', text)
        if match:
            return match.group(1).strip()
        return "未命名作品"


    def _load_project_from_session(self):
        """从会话加载项目"""
        if not self._session_id:
            return
        try:
            from core.lib.session_manager import session_manager
            session = session_manager.validate_session(self._session_id)
            if session:
                context = session.get("context", {})
                if "film_project" in context:
                    data = context["film_project"]
                    self._project = FilmProject(**data)
                    print(f"[Director] 从会话加载项目: {self._project.title}")
        except Exception as e:
            print(f"[Director] 加载项目失败: {e}")

    def _save_project_to_session(self):
        """保存项目到会话"""
        if not self._session_id or not self._project:
            return
        try:
            from core.lib.session_manager import session_manager
            session = session_manager.validate_session(self._session_id)
            if session:
                session["context"]["film_project"] = self._project.__dict__
        except Exception as e:
            print(f"[Director] 保存项目失败: {e}")

    def _call_llm(self, prompt: str, task_type: str = "default") -> str:
        config = self._llm_configs.get(task_type, self._llm_configs["default"])
        num_predict = config.get("num_predict", 2048)
        temperature = config.get("temperature", 0.7)

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
                            "temperature": temperature,
                            "num_predict": num_predict,
                            "top_p": 0.9,
                        }
                    },
                    timeout=120
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")
            except Exception as e:
                print(f"[Director] 尝试 {attempt+1} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def _detect_genre(self, text: str) -> str:
        """检测电影类型"""
        for genre in self.GENRES:
            if genre in text:
                return genre
        return "剧情"


if __name__ == "__main__":
    agent = DirectorAgentV4("test")
    print("=" * 60)
    print("DirectorAgent 完整测试")
    print("=" * 60)

    result = agent.process("创建项目 科幻电影 星际穿越", {"session_id": "test_session"})
    print(result.get("response"))
