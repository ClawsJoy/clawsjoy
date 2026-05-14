#!/usr/bin/env python3
"""ClawsJoy 执行引擎适配器"""

import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ExecutorAdapter(ABC):
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass


class OpenClawAdapter(ExecutorAdapter):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task.get("prompt", "")
        result = subprocess.run(
            f'openclaw infer model run --model ollama/qwen2.5:3b --prompt "{prompt}"',
            shell=True,
            capture_output=True,
            text=True,
        )
        return {"success": True, "output": result.stdout, "engine": "openclaw"}

    def get_capabilities(self) -> List[str]:
        return ["chat", "code", "general"]


class ClaudeCodeAdapter(ExecutorAdapter):
    def __init__(self, workspace_path: str = "/root/clawsjoy"):
        self.workspace = workspace_path
        self.available = shutil.which("claude") is not None

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task.get("prompt", "")
        task_type = task.get("task_type", "code")

        if not self.available:
            return {
                "success": False,
                "error": "Claude Code not installed",
                "engine": "claude_code",
            }

        if task_type in ["code_generation", "code_review", "debug", "write_code"]:
            try:
                cmd = f'cd {self.workspace} && claude -p "{prompt}"'
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=60
                )
                return {
                    "success": result.returncode == 0,
                    "output": (
                        result.stdout if result.returncode == 0 else result.stderr
                    ),
                    "engine": "claude_code",
                }
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Timeout", "engine": "claude_code"}

        return {
            "success": False,
            "error": f"Task {task_type} not suitable",
            "engine": "claude_code",
        }

    def get_capabilities(self) -> List[str]:
        return ["code_generation", "code_review", "debug", "write_code"]


class ExecutorRouter:
    def __init__(self):
        self.engines = {
            "openclaw": OpenClawAdapter(),
            "claude_code": ClaudeCodeAdapter(),
        }

    def route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type", "general")

        if task_type in ["code_generation", "code_review", "debug", "write_code"]:
            result = self.engines["claude_code"].execute(task)
            if result.get("success"):
                return result

        return self.engines["openclaw"].execute(task)

    def list_engines(self) -> Dict:
        return {
            name: engine.get_capabilities() for name, engine in self.engines.items()
        }


if __name__ == "__main__":
    router = ExecutorRouter()
    print("可用引擎:", router.list_engines())


class ExecutorRouterWithConfig(ExecutorRouter):
    def __init__(self, config_path: str = "/mnt/d/clawsjoy/config/engine.json"):
        super().__init__()
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        import json

        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        except:
            self.config = {"executor": "openclaw", "fallback": "self"}

    def route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        preferred = self.config.get("executor", "openclaw")
        fallback = self.config.get("fallback", "self")

        # 尝试首选引擎
        if preferred in self.engines:
            result = self.engines[preferred].execute(task)
            if result.get("success"):
                return result

        # 降级到备用引擎
        if fallback in self.engines:
            return self.engines[fallback].execute(task)

        # 最终降级到 openclaw
        return self.engines["openclaw"].execute(task)


if __name__ == "__main__":
    router = ExecutorRouterWithConfig()
    print("配置:", router.config)
    print("可用引擎:", router.list_engines())
