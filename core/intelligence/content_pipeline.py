#!/usr/bin/env python3
"""Content Pipeline - Content Pipeline 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

from core.lib.unified_config import unified_config

sys.path.insert(0, smart_config.ROOT)

from agent_core.brain_enhanced import brain as brain_core


class Stage(Enum):
    COLLECT = "collect"
    ANALYZE = "analyze"
    COPYWRITE = "copywrite"
    REVIEW_1 = "review_1"
    SCRIPT = "script"
    VIDEO = "video"
    REVIEW_2 = "review_2"
    DONE = "done"


class ContentPipeline:
    """内容生产流水线"""

    def __init__(self):
        self.projects = []
        self.pipeline_file = Path(
            f"{config_helper.get_data_root()}/content_pipeline.json"
        )
        self.load_pipeline()

        print("\n" + "=" * 60)
        print("📹 内容生产流水线")
        print("=" * 60)
        print("采集 → 分析 → 文案 → 初审 → 脚本 → 视频 → 终审")
        print("=" * 60)

    def load_pipeline(self):
        """加载流水线"""
        if self.pipeline_file.exists():
            with open(self.pipeline_file, "r") as f:
                self.projects = json.load(f)

    def save_pipeline(self):
        """保存流水线"""
        with open(self.pipeline_file, "w") as f:
            json.dump(self.projects, f, indent=2)

    def create_project(self, title, source_material):
        """创建项目"""
        project = {
            "id": len(self.projects) + 1,
            "title": title,
            "source_material": source_material,
            "stage": Stage.COLLECT.value,
            "created_at": datetime.now().isoformat(),
            "history": [],
            "scores": {},
        }

        self.projects.append(project)
        self.save_pipeline()
        print(f"✅ 项目创建: {title} (ID: {project['id']})")
        return project

    def advance_stage(self, project_id, result_data=None):
        """推进阶段"""
        project = self.get_project(project_id)
        if not project:
            return None

        current = Stage(project["stage"])
        next_stage = self.get_next_stage(current)

        if result_data:
            project["history"].append(
                {
                    "stage": current.value,
                    "result": result_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        project["stage"] = next_stage.value if next_stage else Stage.DONE.value

        self.save_pipeline()

        print(f"📦 项目 {project_id} 前进: {current.value} → {project['stage']}")
        return project

    def get_next_stage(self, current):
        """获取下一阶段"""
        stages = list(Stage)
        idx = stages.index(current)
        if idx + 1 < len(stages):
            return stages[idx + 1]
        return None

    def get_project(self, project_id):
        """获取项目"""
        for p in self.projects:
            if p["id"] == project_id:
                return p
        return None

    def review_and_score(self, project_id, stage, score, feedback):
        """审核并打分（你做）"""
        project = self.get_project(project_id)
        if not project:
            return None

        project["scores"][stage] = {
            "score": score,  # 1-10分
            "feedback": feedback,
            "reviewer": "flybo",
            "timestamp": datetime.now().isoformat(),
        }

        # 记录到大脑学习
        brain_core.record_experience(
            agent="content_pipeline",
            action=f"review_{stage}",
            result={"score": score},
            context=feedback[:200],
        )

        print(f"⭐ {project['title']} - {stage}: {score}/10")
        print(f"💬 反馈: {feedback}")

        self.save_pipeline()
        return project

    def get_projects_by_stage(self, stage):
        """按阶段获取项目"""
        return [p for p in self.projects if p.get("stage") == stage]

    def show_dashboard(self):
        """显示审核看板"""
        print("\n" + "=" * 60)
        print("📊 内容审核看板")
        print("=" * 60)

        stages = [
            "review_1",
            "review_2",
            "collect",
            "analyze",
            "copywrite",
            "script",
            "video",
        ]

        for stage in stages:
            projects = self.get_projects_by_stage(stage)
            if projects:
                print(f"\n📌 {stage.upper()}: {len(projects)} 个待审核")
                for p in projects[:3]:
                    score_info = p["scores"].get(stage, {})
                    score = score_info.get("score", "未审核")
                    print(f"   [{p['id']}] {p['title'][:30]} - 评分: {score}")

        print("\n" + "=" * 60)

    def auto_advance_approved(self, min_score=7):
        """自动推进已审核通过的项目"""
        for project in self.projects:
            current = project["stage"]
            if current in ["review_1", "review_2"]:
                score_info = project["scores"].get(current, {})
                score = score_info.get("score", 0)
                if score >= min_score:
                    self.advance_stage(
                        project["id"], {"auto_approved": True, "score": score}
                    )
                    print(f"✅ 项目 {project['id']} 自动推进（评分 {score}）")


# CLI 交互界面
class PipelineCLI:
    def __init__(self):
        self.pipeline = ContentPipeline()

    def run(self):
        print("\n📹 内容生产流水线 CLI")
        print("命令: create | list | review | dashboard | advance | exit")

        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "exit":
                    break
                elif cmd[0] == "create":
                    title = input("标题: ")
                    source = input("素材源: ")
                    self.pipeline.create_project(title, source)
                elif cmd[0] == "list":
                    for p in self.pipeline.projects[-10:]:
                        print(f"[{p['id']}] {p['title']} - {p['stage']}")
                elif cmd[0] == "review":
                    pid = int(cmd[1])
                    project = self.pipeline.get_project(pid)
                    if project:
                        print(f"项目: {project['title']}")
                        print(f"当前阶段: {project['stage']}")
                        print(f"素材: {project['source_material'][:200]}")
                        score = int(input("评分 (1-10): "))
                        feedback = input("反馈: ")
                        self.pipeline.review_and_score(
                            pid, project["stage"], score, feedback
                        )
                elif cmd[0] == "dashboard":
                    self.pipeline.show_dashboard()
                elif cmd[0] == "advance":
                    pid = int(cmd[1])
                    self.pipeline.advance_stage(pid)
                else:
                    print("未知命令")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    cli = PipelineCLI()
    cli.run()
