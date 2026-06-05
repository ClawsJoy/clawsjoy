#!/usr/bin/env python3
"""
统一技能注册中心更新脚本 v1.0
ClawsJoy 技能注册中心同步工具
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml


class UnifiedSkillRegistryUpdater:
    """统一技能注册中心更新器"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.skills_dir = self.base_dir / "skills"
        self.config_dir = self.base_dir / "config"
        self.data_dir = self.base_dir / "data"

        self.category_config = self.config_dir / "skill_categories.yaml"
        self.skill_registry = self.data_dir / "skill_registry_v2.json"
        self.skill_manifests = self.data_dir / "skill_manifests.json"
        self.version_registry = self.config_dir / "version_registry.yaml"

        self.backup_dir = (
            self.base_dir
            / "backups"
            / f"registry_backup_{datetime.now():%Y%m%d_%H%M%S}"
        )

        self.category_names = {
            "core": "核心调度",
            "math": "数学计算",
            "text": "文本处理",
            "audio": "音频处理",
            "image": "图像处理",
            "video": "视频制作",
            "network": "网络服务",
            "memory": "记忆系统",
            "self_heal": "自愈系统",
            "tools": "工具集",
            "wrappers": "包装器",
            "auto_generated": "自动生成",
            "development": "开发工具",
            "finance": "投资理财",
            "health": "健康监测",
            "education": "儿童教育",
            "travel": "旅游出行",
            "home": "家庭生活",
            "data": "数据处理",
            "todo": "待办事项",
            "time": "时间日期",
            "text_basic": "文本处理基础",
            "shopping": "购物消费",
            "sales": "销售管理",
            "safety": "家庭安全",
            "reading": "读书学习",
            "math_basic": "数学基础",
            "marketing": "市场分析",
            "food": "美食餐饮",
            "file": "文件操作",
            "digital_employee": "数字员工",
            "crm": "客户管理",
            "course": "课程学习",
            "childcare": "儿童陪护",
            "website": "网站维护",
            "tutoring": "作业辅导",
            "system": "系统信息",
            "study_plan": "学习计划",
            "sports": "健康运动",
            "social": "社交沟通",
            "school": "家校沟通",
            "schedule": "日程管理",
            "random": "随机生成",
            "note": "笔记管理",
            "network_basic": "网络请求",
            "meeting": "会议管理",
            "hr": "人力资源",
            "game": "娱乐游戏",
            "focus": "专注训练",
            "extracurricular": "课外拓展",
            "exam": "考试准备",
            "entertainment": "家庭娱乐",
            "document": "文档管理",
            "brand": "品牌管理",
            "weather": "天气查询",
            "translate": "翻译服务",
            "security": "安全工具",
            "reminder": "提醒服务",
            "news": "新闻资讯",
            "email": "邮件服务",
            "convert": "单位换算",
            "calculator": "计算器",
        }

    def backup_registry_files(self):
        print(f"\n📦 备份到: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        for f in [self.category_config, self.skill_registry, self.skill_manifests]:
            if f.exists():
                shutil.copy2(f, self.backup_dir / f.name)
                print(f"  ✅ 备份: {f.name}")
        return True

    def scan_skill_directories(self) -> Dict[str, List[str]]:
        print("\n🔍 扫描技能目录...")
        skill_categories = {}
        for d in self.skills_dir.iterdir():
            if not d.is_dir() or d.name.startswith("__"):
                continue
            skill_files = [f.stem for f in d.glob("*.py") if f.stem != "__init__"]
            if skill_files:
                skill_categories[d.name] = sorted(skill_files)
        print(
            f"  📊 发现 {len(skill_categories)} 个分类，共 {sum(len(v) for v in skill_categories.values())} 个技能"
        )
        return skill_categories

    def update_category_config(
        self, skill_categories: Dict[str, List[str]]
    ) -> List[str]:
        print("\n📝 更新 skill_categories.yaml...")
        with open(self.category_config, "r") as f:
            config = yaml.safe_load(f)
        current = config.get("categories", {})
        added = []
        for cat in skill_categories.keys():
            if cat not in current:
                current[cat] = self.category_names.get(
                    cat, cat.replace("_", " ").title()
                )
                added.append(cat)
        config["categories"] = dict(sorted(current.items()))
        with open(self.category_config, "w") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        print(f"  ✅ 原有: {len(current)-len(added)}, 新增: {len(added)}")
        return added

    def update_skill_registry_v2(self, skill_categories: Dict[str, List[str]]) -> int:
        print("\n📝 更新 skill_registry_v2.json...")
        registry = {}
        if self.skill_registry.exists():
            with open(self.skill_registry, "r") as f:
                registry = json.load(f)
        existing = set(registry.keys())
        added = []
        for cat, skills in skill_categories.items():
            for skill in skills:
                if skill not in registry:
                    registry[skill] = {
                        "name": skill,
                        "category": cat,
                        "version": "1.0.0",
                        "enabled": True,
                        "created_at": datetime.now().isoformat(),
                    }
                    added.append(skill)
        with open(self.skill_registry, "w") as f:
            json.dump(registry, f, indent=2)
        print(f"  ✅ 原有: {len(existing)}, 新增: {len(added)}")
        return len(added)

    def update_skill_manifests(self, skill_categories: Dict[str, List[str]]) -> int:
        print("\n📝 更新 skill_manifests.json...")
        manifests = {}
        if self.skill_manifests.exists():
            with open(self.skill_manifests, "r") as f:
                manifests = json.load(f)
        existing = set(manifests.keys())
        added = []
        for cat, skills in skill_categories.items():
            for skill in skills:
                if skill not in manifests:
                    manifests[skill] = {
                        "name": skill,
                        "type": "atomic",
                        "version": "1.0.0",
                        "description": f"{self.category_names.get(cat, cat)}技能",
                        "category": cat,
                        "author": "ClawsJoy",
                        "tags": [],
                        "input_schema": {},
                        "output_schema": {},
                        "steps": [],
                        "dependencies": [],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "status": "active",
                        "success_rate": 0.0,
                        "execution_count": 0,
                    }
                    added.append(skill)
        with open(self.skill_manifests, "w") as f:
            json.dump(manifests, f, indent=2)
        print(f"  ✅ 原有: {len(existing)}, 新增: {len(added)}")
        return len(added)

    def trigger_knowledge_sync(self) -> bool:
        print("\n🔄 触发知识库同步...")
        try:
            import requests

            resp = requests.post("http://localhost:5002/api/knowledge/sync", timeout=10)
            if resp.status_code == 200:
                print(f"  ✅ 同步成功")
                return True
        except Exception as e:
            print(
                f"  ⚠️ 请手动执行: curl -X POST http://localhost:5002/api/knowledge/sync"
            )
        return False

    def run(self):
        print("=" * 60)
        print("ClawsJoy 统一技能注册中心更新脚本 v1.0")
        print("=" * 60)
        self.backup_registry_files()
        skill_categories = self.scan_skill_directories()
        if not skill_categories:
            print("❌ 未发现技能目录")
            return
        added_cats = self.update_category_config(skill_categories)
        added_reg = self.update_skill_registry_v2(skill_categories)
        added_man = self.update_skill_manifests(skill_categories)
        self.trigger_knowledge_sync()
        print("\n" + "=" * 60)
        print(
            f"✅ 完成! 技能分类: {len(skill_categories)}, 技能总数: {sum(len(v) for v in skill_categories.values())}"
        )
        print(
            f"   新增分类: {len(added_cats)}, 新增注册: {added_reg}, 新增清单: {added_man}"
        )
        print(f"   备份: {self.backup_dir}")
        print("\n🔧 下一步: curl -X POST http://localhost:5002/api/skills/reload")
        print("=" * 60)


if __name__ == "__main__":
    updater = UnifiedSkillRegistryUpdater()
    updater.run()
