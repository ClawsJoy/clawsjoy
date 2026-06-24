#!/usr/bin/env python3
"""DirectorAgent v6.0 - 电影制作导演"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

from core.agents.business.business_agent import BusinessAgent


@dataclass
class FilmProject:
    title: str = ""
    genre: str = "剧情"
    status: str = "concept"
    progress: int = 0
    script: str = ""
    characters: list = field(default_factory=list)
    scenes: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1


class DirectorAgentV4(BusinessAgent):
    name = "director_agent_v4"
    description = "电影制作导演"
    version = "6.0.0"

    GENRES = ["动作", "喜剧", "剧情", "科幻", "奇幻", "悬疑", "爱情", "动画", "纪录片", "恐怖", "冒险"]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._project: Optional[FilmProject] = None
        print(f"🎬 DirectorAgent v{self.version}")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()

        if "创建" in t or "新项目" in t:
            return self._create(user_input)
        if not self._project:
            return self._resp("请先创建项目。输入「创建 电影名 类型」开始。\n\n示例：创建 星际迷航 科幻")

        if "剧本" in t or "写" in t:
            return self._script(user_input)
        elif "角色" in t:
            return self._characters(user_input)
        elif "场景" in t or "分镜" in t:
            return self._scenes(user_input)
        elif "审查" in t or "评估" in t:
            return self._review()
        elif "修改" in t or "精炼" in t or "优化" in t:
            return self._refine(user_input)
        elif "发布" in t or "完成" in t:
            return self._release()
        elif "导出" in t:
            return self._export()
        elif "状态" in t or "进度" in t:
            return self._status()
        else:
            return self._status()

    def _create(self, user_input: str) -> Dict:
        title = self._extract_title(user_input)
        genre = "剧情"
        for g in self.GENRES:
            if g in user_input:
                genre = g
                break
        self._project = FilmProject(title=title, genre=genre)
        return self._resp(f"## 🎬 项目创建成功\n\n**{title}** | {genre} | 概念阶段\n\n💡 输入「写剧本」开始创作")

    def _script(self, user_input: str) -> Dict:
        prompt = f"为电影《{self._project.title}》创作完整剧本。类型：{self._project.genre}。要求：三幕结构、场景标题、动作描述、角色对白、2000-4000字。"
        result = self._call_llm(prompt, task_type="script", max_tokens=4096)
        if result:
            self._project.script = result
            self._project.progress = 25
            self._project.version += 1
            self._project.updated_at = datetime.now().isoformat()
            return self._resp(f"## ✍️ 剧本完成\n\n进度25% | {len(result)}字 | v{self._project.version}\n\n{result[:800]}...")
        return self._resp("剧本生成失败")

    def _characters(self, user_input: str) -> Dict:
        prompt = f"为《{self._project.title}》设计主要角色。类型：{self._project.genre}。要求：主角(姓名/年龄/性格/动机/弧光)、配角2-3个、反派、角色关系网。"
        result = self._call_llm(prompt, task_type="character")
        if result:
            self._project.characters.append({"content": result})
            self._project.progress = max(self._project.progress, 35)
            return self._resp(f"## 🎭 角色设定\n\n{result}")
        return self._resp("角色设定失败")

    def _scenes(self, user_input: str) -> Dict:
        prompt = f"为《{self._project.title}》设计5-8个关键场景。每个场景：地点/时间/事件/角色/情绪基调/冲突密度(1-10)。"
        result = self._call_llm(prompt, task_type="scene")
        if result:
            self._project.scenes.append({"content": result})
            self._project.progress = max(self._project.progress, 45)
            return self._resp(f"## 🎨 场景设计\n\n{result}")
        return self._resp("场景设计失败")

    def _review(self) -> Dict:
        if not self._project.script:
            return self._resp("请先生成剧本")
        prompt = f"审查以下剧本，从结构/角色/对白/节奏/主题五个维度评分(1-10)并给出改进建议：\n\n{self._project.script[:3000]}"
        result = self._call_llm(prompt, task_type="review")
        return self._resp(f"## 📊 剧本审查\n\n{result}" if result else "审查失败")

    def _refine(self, user_input: str) -> Dict:
        feedback = re.sub(r'^(修改|精炼|优化)', '', user_input).strip()
        if not feedback:
            return self._resp("请说明修改意见。例如：精炼 主角对话更幽默")
        prompt = f"根据反馈修改剧本，保持整体结构不变：\n\n反馈：{feedback}\n\n剧本：{self._project.script[:3000]}"
        result = self._call_llm(prompt, task_type="refine")
        if result:
            self._project.script = result
            self._project.version += 1
            self._project.updated_at = datetime.now().isoformat()
            return self._resp(f"## ✅ 精炼完成 v{self._project.version}\n\n{result[:800]}...")
        return self._resp("精炼失败")

    def _release(self) -> Dict:
        self._project.status = "released"
        self._project.progress = 100
        self._project.updated_at = datetime.now().isoformat()
        return self._resp(f"## 🚀 发布完成\n\n**{self._project.title}** | {self._project.genre} | {len(self._project.script)}字")

    def _export(self) -> Dict:
        path = f"/tmp/{self._project.title}_剧本.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._project.script)
        return self._resp(f"✅ 已导出到 {path}（{len(self._project.script)}字）")

    def _status(self) -> Dict:
        p = self._project
        return self._resp(f"**{p.title}** | {p.genre} | {p.status} | {p.progress}% | {len(p.script)}字 | v{p.version}")

    def _extract_title(self, text: str) -> str:
        for g in self.GENRES:
            text = text.replace(g, "")
        text = re.sub(r'(创建|新项目|电影|项目|一部)', '', text).strip()
        return text[:30] if text else "未命名作品"

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = DirectorAgentV4("test")
    print(agent.process("创建 星际迷航 科幻")["response"][:200])
