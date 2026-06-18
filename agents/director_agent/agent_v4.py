#!/usr/bin/env python3
"""DirectorAgent v4.2 - 精简稳定版（电影制作管理）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field

from core.agents.business.business_agent import BusinessAgent


@dataclass
class FilmProject:
    id: str
    title: str
    genre: str
    status: str
    progress: int
    script: str = ""
    characters: List[Dict] = field(default_factory=list)
    scenes: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DirectorAgentV4(BusinessAgent):
    """导演 Agent - 精简稳定版"""

    name = "director_agent_v4"
    description = "电影制作导演"
    version = "4.2.0"

    GENRES = ["动作", "喜剧", "剧情", "科幻", "奇幻", "悬疑", "爱情", "动画", "纪录片"]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._session_id = None
        self._project: Optional[FilmProject] = None
        self._llm_model = "qwen2.5:7b"
        self._max_retries = 2
        print(f"🎬 DirectorAgent v{self.version} 启动")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
            self._load_project_from_session()
        return super().process(user_input, context)

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["创建", "新项目", "拍电影", "制作电影"]):
            return self._handle_create(user_input)
        if any(kw in t for kw in ["写剧本", "剧本"]):
            return self._handle_script()
        if any(kw in t for kw in ["角色", "人物"]):
            return self._handle_characters()
        if any(kw in t for kw in ["场景", "分镜"]):
            return self._handle_scenes()
        if any(kw in t for kw in ["审查", "质量", "评价"]):
            return self._handle_review()
        if any(kw in t for kw in ["精炼", "优化", "修改"]):
            return self._handle_refine(user_input)
        if any(kw in t for kw in ["导出", "export"]):
            return self._handle_export()
        if any(kw in t for kw in ["状态", "进度"]):
            return self._handle_status()
        if any(kw in t for kw in ["发布", "上映"]):
            return self._handle_release()
        
        return self._resp("我是导演助手。输入「创建项目」、「写剧本」、「设定角色」、「设计场景」、「审查剧本」、「精炼剧本」、「导出剧本」或「项目状态」。")

    # ================================================================
    #  项目管理
    # ================================================================

    def _handle_create(self, user_input: str) -> Dict:
        title = self._extract_title(user_input)
        genre = self._detect_genre(user_input)
        
        self._project = FilmProject(
            id=f"film_{int(time.time())}",
            title=title,
            genre=genre,
            status="concept",
            progress=0
        )
        self._save_project_to_session()
        
        return self._resp(f"""
## 🎬 项目创建成功

**标题**: {title}
**类型**: {genre}
**状态**: 概念开发
**进度**: 0%

💡 输入「写剧本」开始创作
""")

    def _handle_status(self) -> Dict:
        if not self._project:
            return self._resp("暂无项目。输入「创建项目」开始。")
        
        p = self._project
        return self._resp(f"""
## 📊 项目状态

**标题**: {p.title}
**类型**: {p.genre}
**状态**: {p.status}
**进度**: {p.progress}%

剧本: {len(p.script)} 字符
角色: {len(p.characters)} 个
场景: {len(p.scenes)} 个
""")

    def _handle_release(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        
        self._project.status = "released"
        self._project.progress = 100
        self._save_project_to_session()
        
        return self._resp(f"""
## 🚀 发布完成！

**{self._project.title}** 已上映 🎉

📊 剧本: {len(self._project.script)} 字符
🎭 角色: {len(self._project.characters)} 个
🎨 场景: {len(self._project.scenes)} 个
""")

    # ================================================================
    #  剧本
    # ================================================================

    def _handle_script(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        
        prompt = f"""
为电影《{self._project.title}》创作完整剧本：

类型: {self._project.genre}

要求：三幕结构、场景标题、动作描述、对白、角色弧光、情感高潮

输出标准剧本格式。
"""
        script = self._call_llm(prompt)
        if script:
            self._project.script = script
            self._project.progress = 25
            self._save_project_to_session()
            return self._resp(f"## ✍️ 剧本完成\n\n{script[:500]}...\n\n📊 进度: 25%")
        
        return self._resp("剧本生成失败，请重试。")

    # ================================================================
    #  角色
    # ================================================================

    def _handle_characters(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        
        prompt = f"""
为电影《{self._project.title}》设计主要角色：

类型: {self._project.genre}

要求：主角、配角、反派，每个角色包含：姓名、性格、动机、背景
"""
        result = self._call_llm(prompt)
        if result:
            self._project.characters.append({"content": result})
            self._project.progress = 35
            self._save_project_to_session()
            return self._resp(f"## 🎭 角色设定完成\n\n{result}\n\n📊 进度: 35%")
        
        return self._resp("角色设定失败，请重试。")

    # ================================================================
    #  场景
    # ================================================================

    def _handle_scenes(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        
        prompt = f"""
为电影《{self._project.title}》设计关键场景：

类型: {self._project.genre}
剧本: {self._project.script[:500]}...

要求：5-8个场景，包含地点、时间、主要事件
"""
        result = self._call_llm(prompt)
        if result:
            self._project.scenes.append({"content": result})
            self._project.progress = 45
            self._save_project_to_session()
            return self._resp(f"## 🎨 场景设计完成\n\n{result}\n\n📊 进度: 45%")
        
        return self._resp("场景设计失败，请重试。")

    # ================================================================
    #  审查
    # ================================================================

    def _handle_review(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        if not self._project.script:
            return self._resp("请先生成剧本。")
        
        prompt = f"""
审查以下剧本（1-10分）：

{self._project.script[:3000]}

维度：结构完整性、角色一致性、对白质量、节奏控制、主题表达

输出评分和改进建议。
"""
        review = self._call_llm(prompt)
        return self._resp(f"## 📊 审查报告\n\n{review}")

    # ================================================================
    #  精炼
    # ================================================================

    def _handle_refine(self, user_input: str) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        if not self._project.script:
            return self._resp("请先生成剧本。")
        
        feedback = re.sub(r'^(精炼|优化|修改|改进)', '', user_input).strip()
        if not feedback:
            return self._resp("请说明修改意见。例如：精炼 主角对话更幽默")
        
        prompt = f"""
根据反馈修改剧本：

反馈：{feedback}
剧本：{self._project.script[:2000]}

只输出修改后的内容。
"""
        refined = self._call_llm(prompt)
        if refined:
            self._project.script += f"\n\n--- 精炼 ---\n{refined}"
            self._save_project_to_session()
            return self._resp(f"✅ 精炼完成\n\n{refined}")
        
        return self._resp("精炼失败，请重试。")

    # ================================================================
    #  导出
    # ================================================================

    def _handle_export(self) -> Dict:
        if not self._project:
            return self._resp("请先创建项目。")
        if not self._project.script:
            return self._resp("请先生成剧本。")
        
        content = f"""标题：{self._project.title}
类型：{self._project.genre}
状态：{self._project.status}
进度：{self._project.progress}%

{self._project.script}
"""
        filename = f"/tmp/{self._project.title}_script.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        return self._resp(f"✅ 已导出: {filename}")

    # ================================================================
    #  画布节点
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
        script = self._call_llm(prompt)
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
        result = self._call_llm(prompt)
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
        result = self._call_llm(prompt)
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
        review = self._call_llm(prompt)
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
        match = re.search(r'[《「『]\s*(.+?)\s*[》」』]', text)
        if match:
            return match.group(1)
        match = re.search(r'(?:叫|名为|标题)[：:]\s*(.+?)(?:[，,。.!！]|$)', text)
        if match:
            return match.group(1).strip()
        match = re.search(r'(?:创作|制作|拍)\s*(.+?)(?:电影|作品|$)', text)
        if match:
            return match.group(1).strip()
        return "未命名作品"

    def _detect_genre(self, text: str) -> str:
        for genre in self.GENRES:
            if genre in text:
                return genre
        return "剧情"

    def _load_project_from_session(self):
        if not self._session_id:
            return
        try:
            from core.lib.session_manager import session_manager
            session = session_manager.load(self._session_id)
            if session and "film_project" in session.context:
                data = session.context["film_project"]
                self._project = FilmProject(**data)
        except Exception as e:
            print(f"[Director] 加载项目失败: {e}")

    def _save_project_to_session(self):
        if not self._session_id or not self._project:
            return
        try:
            from core.lib.session_manager import session_manager
            session = session_manager.load(self._session_id)
            if session:
                session.set_context("film_project", self._project.__dict__)
                session_manager.save(session)
        except Exception as e:
            print(f"[Director] 保存项目失败: {e}")

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
                print(f"[Director] 尝试 {attempt+1} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = DirectorAgentV4("test")
    print(agent.process("创建项目 科幻电影 星际穿越")["response"])
