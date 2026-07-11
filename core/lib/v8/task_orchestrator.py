#!/usr/bin/env python3
"""
TaskOrchestrator v9.1 — 包工头：任务全生命周期管理

协议：
- 钩子 _on_task_state_change：只做通知 + 触发审查，不做执行调度
- plan / start_next / review_task：显式调用 execute_task
- 返工：review 不通过 → pending → running → execute_task（循环直到通过）
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.lib.llm_client import llm_client
from core.lib.v8.roster_engine import roster_engine
from core.lib.v8.task_engine import task_engine
from core.lib.notify import notify

logger = logging.getLogger(__name__)

MODEL_MAIN = "qwen2.5:7b-instruct-q4_0"

SKILL_TO_POSITION = {
    "代码开发": "程序员", "写代码": "程序员", "编程": "程序员",
    "bug修复": "程序员", "部署": "程序员",
    "数据分析": "分析师", "分析": "分析师", "竞品分析": "分析师",
    "市场调研": "分析师", "搜索": "分析师",
    "内容写作": "作家", "写作": "作家", "写脚本": "作家",
    "写文案": "作家", "撰写": "作家", "创作": "作家",
    "翻译": "翻译员", "多语言": "翻译员",
    "图片分析": "设计师", "设计": "设计师", "画图": "设计师",
    "音频制作": "作家", "音频": "作家", "音效": "作家",
    "视频制作": "视频编辑", "视频剪辑": "视频编辑",
    "文件管理": "文件管理", "文件读写": "文件管理",
    "任务规划": "决策审查", "规划": "决策审查", "审查": "决策审查",
    "财务规划": "分析师", "预算": "分析师",
    "评估": "决策审查",
    "图像生成": "设计师", "导演模式": "设计师", "拍摄计划": "设计师",
    "工作流执行": "程序员",
}

AGENT_TO_POSITION = {
    "writer_agent": "作家", "analysis_agent": "分析师",
    "code_agent": "程序员", "vision_agent": "设计师",
    "video_agent": "视频编辑", "translate_agent": "翻译员",
    "file_agent": "文件管理", "decision_agent": "决策审查",
    "chat_agent": "作家",
}

POSITION_TO_AGENT = {
    "程序员": "code_agent", "分析师": "analysis_agent",
    "作家": "writer_agent", "设计师": "vision_agent",
    "视频编辑": "video_agent", "翻译员": "translate_agent",
    "文件管理": "file_agent", "决策审查": "decision_agent",
}

ORCHESTRATIONS_FILE = Path("data/v8/orchestrations.json")


class TaskOrchestrator:
    """包工头 — plan / execute / review / start_next"""

    def __init__(self):
        self._orchestrations: Dict[str, dict] = {}
        self.knowledge: dict = {}
        self._load_knowledge()
        self._load_orchestrations()
        task_engine.on_state_change(self._on_task_state_change)

    # ====================================================================
    #  知识 & 持久化
    # ====================================================================

    def _load_knowledge(self):
        self.knowledge["agents"] = self._summarize_agents()
        self.knowledge["positions"] = self._summarize_positions()

    def _summarize_agents(self) -> dict:
        summary = {}
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            for name, caps in wisdom_factory.CAPABILITIES.items():
                summary[name] = {"skills": caps}
        except:
            pass
        return summary

    def _summarize_positions(self) -> dict:
        positions = {}
        try:
            import yaml
            pos_dir = Path("config/v8/positions")
            if pos_dir.exists():
                for f in pos_dir.glob("*.yaml"):
                    with open(f) as fp:
                        pos = yaml.safe_load(fp)
                        positions[f.stem] = pos
        except:
            pass
        return positions

    def _load_orchestrations(self):
        if ORCHESTRATIONS_FILE.exists():
            try:
                self._orchestrations = json.loads(ORCHESTRATIONS_FILE.read_text())
            except:
                pass

    def _save_orchestrations(self):
        ORCHESTRATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ORCHESTRATIONS_FILE.write_text(json.dumps(self._orchestrations, ensure_ascii=False, indent=2))

    def _refresh_workers(self, server_id="default"):
        workers = {}
        for m in roster_engine.list_active(server_id):
            budget = roster_engine.check_budget(server_id, m["name"])
            workers[m["name"]] = {
                "position": m.get("position", ""),
                "status": m.get("status", "active"),
                "budget_remaining": budget.get("remaining", 0),
                "task_count": m.get("task_count", 0),
            }
        self.knowledge["workers"] = workers

    # ====================================================================
    #  状态钩子（只做通知 + 触发审查，不做执行调度）
    # ====================================================================

    def _on_task_state_change(self, task_id, old_state, new_state, task_data):
        executor = task_data.get("assigned_to", "")
        title = task_data.get("title", "")

        if new_state == "running":
            notify(executor, f"开始执行「{title}」")

        elif new_state == "done":
            notify(executor, f"「{title}」已完成")
            self.review_task(task_id, task_data)

        elif new_state == "reviewed":
            output = task_data.get("output", "")
            if output:
                notify("老板", f"✅「{title}」已完成\n{output[:1500]}")
            else:
                notify("老板", f"✅「{title}」审查通过")

        elif new_state == "failed":
            notify("老板", f"「{title}」执行失败")

    # ====================================================================
    #  Plan
    # ====================================================================

    def plan(self, user_input: str, user_id: str,
             channel_id: str = "", server_id: str = "default") -> dict:
        self._refresh_workers(server_id)

        project_dir = Path(f"data/projects/{user_id}")
        has_brief = False
        if project_dir.exists():
            has_brief = any(project_dir.rglob("BRIEF.md"))
        if not has_brief:
            template_dir = Path("config/templates/project")
            if template_dir.exists():
                import shutil
                shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)
                brief_file = project_dir / "BRIEF.md"
                if brief_file.exists():
                    content = brief_file.read_text()
                    content = content.replace("{项目名称}", user_input[:30])
                    content = content.replace("{老板的原始需求}", user_input)
                    brief_file.write_text(content)

        subtasks = self._decompose(user_input)
        if not subtasks:
            return {"success": False, "response": "无法拆解需求，请提供更具体的描述。"}

        active_agents = roster_engine.list_active(server_id)
        created_tasks = []
        for sub in subtasks:
            agent = self._find_worker(sub.get("required_skill", ""), active_agents)
            if not agent:
                continue
            task = task_engine.create(
                server_id=server_id,
                title=sub["title"],
                assigned_to=agent["name"],
                assigned_position=agent.get("position", ""),
                created_by=user_id,
                priority="high" if len(created_tasks) == 0 else "normal",
            )
            task["_skill"] = sub.get("required_skill", "")
            task["_agent_name"] = agent["name"]
            task["_step"] = len(created_tasks) + 1
            task["_channel_id"] = channel_id
            task["output_file"] = sub.get("output_file") or self._generate_output_file(sub["title"], len(created_tasks))
            created_tasks.append(task)

        if not created_tasks:
            return {"success": False, "response": "当前无可用工人执行此任务，请先聘用对应岗位。"}

        self._orchestrations[user_id] = {
            "input": user_input,
            "task_ids": [t["id"] for t in created_tasks],
            "total": len(created_tasks),
            "created_at": datetime.now().isoformat(),
        }
        self._save_orchestrations()

        card = self._build_card(created_tasks, user_input)

        # 显式启动第一个
        first_task = created_tasks[0]
        task_engine.transition(server_id, first_task["id"], "running", "自动开始")
        self.execute_task(first_task)

        agent_name = first_task.get("_agent_name", "待分配")
        next_hint = ""
        if len(created_tasks) > 1:
            next_hint = f"\n\n📌 下一步：**{created_tasks[1]['title']}**（完成后自动开始）"

        return {
            "success": True,
            "response": card + f"\n\n▶️ 第1步「{first_task['title']}」已启动 → @{agent_name}{next_hint}",
            "method": "planned",
            "intent": "plan",
            "confidence": 0.90,
            "agents_used": [t.get("_agent_name", "") for t in created_tasks],
            "tasks": created_tasks,
            "tokens": 0,
            "model": "orchestrator",
        }

    # ====================================================================
    #  Execute
    # ====================================================================

    def execute_task(self, task_data, server_id="default"):
        title = task_data.get("title", "")
        worker = task_data.get("assigned_to", "")
        position = task_data.get("assigned_position", "")
        created_by = task_data.get("created_by", "")

        if not worker:
            task_engine.transition(server_id, task_data["id"], "failed", "无执行者")
            return

        # 花名册覆盖：有 api_key 走适配器
        member = roster_engine.get(server_id, worker)
        if member and member.get("api_key"):
            try:
                from core.lib.v8.adapters.factory import get_adapter
                adapter = get_adapter(member.get("model", ""), api_key=member["api_key"])
                if adapter:
                    result = adapter.execute(f"任务：{title}")
                    if result.get("success"):
                        task_data["output"] = result["content"][:2000]
                        task_engine.transition(server_id, task_data["id"], "done", "执行完成")
                        return
            except Exception as e:
                logger.warning(f"适配器执行失败: {e}")

        agent_type = POSITION_TO_AGENT.get(position, "chat_agent")

        original_input = ""
        for uid, state in self._orchestrations.items():
            if task_data["id"] in state.get("task_ids", []):
                original_input = state.get("input", "")
                break

        rules = ""
        try:
            rules_path = Path("config/RULES.md")
            if rules_path.exists():
                rules = rules_path.read_text()
        except:
            pass

        brief_content = ""
        try:
            user_project_dir = Path(f"data/projects/{created_by}")
            if user_project_dir.exists():
                for brief_file in user_project_dir.rglob("BRIEF.md"):
                    brief_content += brief_file.read_text() + "\n"
                    spec_dir = brief_file.parent / "specs"
                    if spec_dir.exists():
                        for spec_file in spec_dir.glob("*.md"):
                            brief_content += f"\n---\n{spec_file.read_text()}\n"
                    break
        except:
            pass

        # 在 prompt 拼接之前注入前序文件
        previous_files = ""
        try:
            user_project_dir = Path(f"data/projects/{created_by}")
            if user_project_dir.exists():
                for brief_file in user_project_dir.rglob("BRIEF.md"):
                    project_dir = brief_file.parent
                    all_tasks = task_engine.list(server_id)
                    for t in all_tasks:
                        if t.get("created_by") == created_by and t.get("output_file"):
                            prev_path = project_dir / t["output_file"]
                            if prev_path.exists():
                                previous_files += f"\n【前序任务：{t['title']}】\n{prev_path.read_text()[:1000]}\n"
                    break
        except:
            pass

        prompt = f"""【你的身份】
你是 ClawsJoy 的 {position}。

【规则】
直接产出，不要反问，不要建议过程。不确定的标注"待确认"。

【项目背景】
ClawsJoy 是一个本地 AI 劳动力管理平台。一人公司老板在 Discord 频道里聘 AI 员工、分配任务、自动协作。核心功能：AI 劳动力管理、Discord 频道协作、自动记账。

{previous_files}

【你的任务】
{title}

【验收标准】
{brief_content}

直接产出最终交付物。这是独立文件，不要重复前序已产出的内容。使用 Markdown 表格。不要复述规则和背景。""" 
        
        result = {}
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            agent = wisdom_factory.get_agent(agent_type, f"worker_{worker}")
            result = agent.process(user_input=prompt, context={
                "skip_intent": True,
                "task_id": task_data["id"],
                "created_by": created_by,
                "server_id": server_id,
                "channel_id": task_data.get("_channel_id", ""),
            })
        except Exception as e:
            logger.warning(f"执行失败: {e}")

        if result.get("success") and result.get("response"):
            task_data["output"] = result["response"][:2000]

            output_file = task_data.get("output_file", "")
            if output_file and created_by:
                try:
                    user_project_dir = Path(f"data/projects/{created_by}")
                    if user_project_dir.exists():
                        for brief_file in user_project_dir.rglob("BRIEF.md"):
                            out_path = brief_file.parent / output_file
                            out_path.write_text(result["response"])
                            break
                except:
                    pass

            data = task_engine._load(server_id)
            if task_data["id"] in data["tasks"]:
                data["tasks"][task_data["id"]]["output"] = result["response"][:2000]
            task_engine._save(server_id, data)
            task_engine.transition(server_id, task_data["id"], "done", "执行完成")
            return

        task_engine.transition(server_id, task_data["id"], "failed", "执行失败")


    # ====================================================================
    #  Review
    # ====================================================================
    def review_task(self, task_id, task_data, server_id="default"):
        title = task_data.get("title", "")
        created_by = task_data.get("created_by", "")
        worker = task_data.get("assigned_to", "")
        output = task_data.get("output", "")

        if not output:
            self.start_next(task_data)
            return

        spec = ""
        try:
            spec_dir = Path(f"data/projects/{created_by}")
            if spec_dir.exists():
                for spec_file in spec_dir.rglob("*.md"):
                    spec += spec_file.read_text() + "\n"
        except:
            pass

        retry_count = task_data.get("_retry_count", 0)

        prompt = f"""你是 ClawsJoy 的审查员。对照验收标准，审查以下任务产出。

【验收标准】
{spec}

【任务产出】
{output[:1500]}

请逐项检查，只输出：
通过项：
- ...
修改项：
- ...

如果全部通过，只输出"通过"。不要反问。"""


        try:
            review = llm_client.generate(prompt, task_type="review", timeout=120)
            if review:
                review_dir = Path(f"data/projects/{created_by}/reviews")
                review_dir.mkdir(parents=True, exist_ok=True)
                review_file = review_dir / f"{task_id}_review.md"

                if review.strip().startswith("通过"):
                    task_engine.transition(server_id, task_id, "reviewed", "审查通过")
                    review_file.write_text(f"✅ 审查通过\n\n{review}")
                    self.start_next(task_data)
                elif retry_count >= 2:
                    notify("老板", f"❌「{title}」返工{retry_count}次未通过")
                    with open(review_file, "a") as f:
                        f.write(f"\n---\n❌ 返工{retry_count+1}次，标记失败\n{review}\n")
                    task_engine.transition(server_id, task_id, "failed", "审查多次不通过")
                else:
                    notify(worker, f"🔄「{title}」返工第{retry_count+1}次")
                    with open(review_file, "a") as f:
                        f.write(f"\n---\n🔄 返工第{retry_count+1}次\n{review}\n")
                    task_data["_retry_count"] = retry_count + 1
                    print(f"[ORCH] 返工 {worker} {title} 第{retry_count+1}次")
                    task_engine.transition(server_id, task_id, "pending", "审查不通过")
                    task_engine.transition(server_id, task_id, "running", "返工重试")
                    updated_task = task_engine.get(server_id, task_id)
                    self.execute_task(updated_task)
            else:
                print(f"[ORCH] review 为空，跳过审查")
                self.start_next(task_data)
        except Exception as e:
            logger.warning(f"审查失败: {e}")
            self.start_next(task_data)


    # ====================================================================
    #  Start Next
    # ====================================================================

    def start_next(self, task_data, server_id="default"):
        all_tasks = task_engine.list(server_id)
        created_by = task_data.get("created_by", "")

        next_tasks = [
            t for t in all_tasks
            if t.get("created_by") == created_by
            and t["status"] == "pending"
            and t.get("assigned_to")
        ]

        if next_tasks:
            next_tasks.sort(key=lambda t: t.get("created_at", ""))
            next_t = next_tasks[0]
            task_engine.transition(server_id, next_t["id"], "running", "自动开始")
            self.execute_task(next_t)
            return

        orphan = [t for t in all_tasks
                  if t.get("created_by") == created_by
                  and t["status"] == "pending"
                  and not t.get("assigned_to")]
        if orphan:
            names = "、".join([t["title"] for t in orphan])
            notify("老板", f"⚠️ 以下任务无可用工人：{names}")

        notify("老板", "🎉 所有可执行任务已完成！")

    # ====================================================================
    #  拆解
    # ====================================================================

    def _decompose(self, user_input: str) -> List[dict]:
        agent_summary = json.dumps(
            {name: caps.get("skills", []) for name, caps in self.knowledge.get("agents", {}).items()},
            ensure_ascii=False
        )
        active_positions = []
        try:
            for m in roster_engine.list_active("default"):
                active_positions.append(m.get("position", ""))
        except:
            pass
        position_hint = f"当前可用工人岗位：{', '.join(active_positions)}。只拆这些岗位能做的步骤。" if active_positions else ""

        # ================================================================
        # 改 1：_decompose prompt — 每个 task 产出独立文件
        # ================================================================

        prompt = f"""将以下需求拆解为 2-4 个子任务。每个子任务产出一个独立文件，后续任务依赖前序文件。

可用 Agent 能力：
{agent_summary}

{position_hint}

需求：{user_input}

规则：
- 每个子任务产出一个独立文件，文件名根据任务内容用英文命名（如 storyboard.md、visual_style.md、video_script.md、audio_plan.md）
- 后续任务基于前序文件展开，不重复前序内容
- 每个 task 产出物必须不同，不要拆出两个相似 task
- 不要把同一工种的工作拆成多个 task
- 视觉/设计类用"图像生成"或"设计"，音频类用"音频制作"，不全部用"内容写作"
- 不要拆出审查、审核、验收步骤
- 标题用"动词+对象"，不含"你们""帮我"
- required_skill 从可用技能中选择：内容写作, 视频制作, 视频剪辑, 图像生成, 翻译, 设计, 音频制作, 数据分析

输出严格 JSON 数组：
[{{"title": "撰写分镜脚本", "required_skill": "内容写作", "output_file": "storyboard.md"}}, ...]"""


        try:
            resp = llm_client.generate(
                prompt, model=MODEL_MAIN, max_tokens=800,
                temperature=0.2, task_type="task_decompose", timeout=30
            )
            resp = resp.strip()
            if "```" in resp:
                match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', resp, re.DOTALL)
                if match:
                    resp = match.group(1)
            if "[" in resp and "]" in resp:
                start = resp.index("[")
                end = resp.rindex("]") + 1
                parsed = json.loads(resp[start:end])
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
        except Exception as e:
            logger.warning(f"LLM 拆解失败: {e}")

        return self._rule_decompose(user_input)

    def _rule_decompose(self, text: str) -> List[dict]:
        parts = re.split(r'[，,；;然后接着再]+', text)
        parts = [p.strip() for p in parts if len(p.strip()) > 3]
        if not parts:
            return [{"title": text[:50], "required_skill": self._guess_skill(text)}]
        return [{"title": p[:50], "required_skill": self._guess_skill(p)} for p in parts[:4]]

    def _guess_skill(self, text: str) -> str:
        for skill in SKILL_TO_POSITION:
            if any(w in text for w in skill):
                return skill
        return "内容写作"

    def _find_worker(self, skill: str, active_agents: List[dict]) -> Optional[dict]:
        target = SKILL_TO_POSITION.get(skill, "")
        if target:
            for a in active_agents:
                if a.get("position") == target:
                    return a
        target = AGENT_TO_POSITION.get(skill, "")
        if target:
            for a in active_agents:
                if a.get("position") == target:
                    return a
        for a in active_agents:
            if a.get("position", "") in skill or skill in a.get("position", ""):
                return a

        # 降级：找不到工人 → 分配给作家
        for a in active_agents:
            if a.get("position") == "作家":
                return a
        return None

    # ====================================================================
    #  Discord
    # ====================================================================

    def _build_card(self, tasks: List[dict], original_input: str) -> str:
        emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        lines = [f"📋 **任务已创建** — 共 {len(tasks)} 步\n"]
        for i, t in enumerate(tasks):
            e = emoji[i] if i < len(emoji) else "▶️"
            lines.append(f"{e} **{t['title']}** → @{t.get('_agent_name', '待分配')}")
        lines.append(f"\n💬 *{original_input[:120]}{'...' if len(original_input) > 120 else ''}*")
        return "\n".join(lines)

    def _generate_output_file(self, title: str, step: int) -> str:
        short = re.sub(r'[^a-zA-Z\u4e00-\u9fa5]', '', title)[:8]
        return f"step{step:02d}_{short}.md"


orchestrator = TaskOrchestrator()
