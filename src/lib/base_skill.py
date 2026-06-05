#!/usr/bin/env python3
"""Base Skill - Base Skill 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""原子技能基类"""
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseAtomicSkill(ABC):
    """原子技能基类 - 所有原子技能必须继承此类"""

    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    category: str = ""
    author: str = "ClawsJoy"

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能 - 子类必须实现"""
        pass

    def validate_input(self, params: Dict) -> bool:
        """验证输入参数"""
        return True

    def log_execution(self, params: Dict, result: Dict):
        """记录执行日志"""
        import datetime

        log_file = Path("logs/skill_execution.log")
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, "a") as f:
            f.write(
                f"{datetime.datetime.now()} | {self.name} | {json.dumps(params)[:100]} | {result.get('success')}\n"
            )

    def get_manifest(self) -> Dict:
        """获取技能清单"""
        return {
            "name": self.name,
            "type": "atomic",
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "author": self.author,
            "compatible_with": ["openclaw", "clawsjoy", "community"],
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
        }

    def get_input_schema(self) -> Dict:
        """获取输入参数定义"""
        return {}

    def get_output_schema(self) -> Dict:
        """获取输出格式定义"""
        return {"success": {"type": "boolean"}}


class BaseWorkflowSkill(BaseAtomicSkill):
    """工作流技能基类"""

    steps: list = []
    dependencies: list = []

    def execute(self, params: Dict) -> Dict:
        """执行工作流 - 自动组合原子技能"""
        context = params.copy()
        results = {}

        for step in self.steps:
            skill_name = step.get("skill")
            step_params = step.get("params", {}).copy()

            # 解析参数中的占位符
            for key, value in step_params.items():
                if isinstance(value, str) and "{" in value:
                    step_params[key] = value.format(**context, **results)

            # 调用原子技能
            result = self._call_atomic_skill(skill_name, step_params)
            output_key = step.get("output", skill_name)
            results[output_key] = result

            if not result.get("success"):
                return {
                    "success": False,
                    "error": f"步骤失败: {skill_name}",
                    "step_result": result,
                }

        return {"success": True, "workflow": self.name, "results": results}

    def _call_atomic_skill(self, name: str, params: Dict) -> Dict:
        """调用原子技能"""
        try:
            module = __import__(
                f"src.skills.atomic.{self._get_skill_path(name)}", fromlist=["skill"]
            )
            if hasattr(module, "skill"):
                return module.skill.execute(params)
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": f"技能 {name} 不存在"}

    def _get_skill_path(self, name: str) -> str:
        """获取技能路径"""
        paths = {
            "script_generator": "text.script_generator",
            "audio_generator": "audio.audio_generator",
            "video_composer": "video.video_composer",
        }
        return paths.get(name, f"text.{name}")
