#!/usr/bin/env python3
"""ExecutorAgent v5.0 - 安全任务执行器"""

import subprocess
import shlex
import io
import contextlib
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class ExecutorAgentV4(BusinessAgent):
    name = "executor_agent_v4"
    description = "安全任务执行器"
    version = "5.0.0"

    ALLOWED_COMMANDS = ["ls", "pwd", "cat", "head", "tail", "grep", "find",
                        "wc", "sort", "echo", "date", "mkdir", "touch", "cp", "mv", "git", "python", "python3"]
    FORBIDDEN = [r"rm\s+-rf\s+/", r"dd\s+if=", r">\s*/dev/", r"mkfs", r"shutdown", r"reboot", r"curl.*\|.*sh"]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.work_dir = Path(f"data/executor/{user_id}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        print(f"⚡ ExecutorAgent v{self.version}")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()

        if t.startswith("exec ") or t.startswith("执行 "):
            return self._exec_cmd(user_input.split(maxsplit=1)[1])
        elif t.startswith("code "):
            return self._exec_code(user_input.split(maxsplit=1)[1])
        elif t.startswith("skill "):
            return self._exec_skill(user_input.split(maxsplit=1)[1])
        elif t.startswith("file "):
            return self._file_op(user_input.split(maxsplit=1)[1])
        elif t.startswith("workflow "):
            return self._exec_workflow(user_input.split(maxsplit=1)[1])
        else:
            # cortex 已匹配 Skill，直接执行
            skill_name = context.get("extracted", {}).get("_skill_name", "") if context else ""
            if skill_name:
                result = self._exec_skill(skill_name)
                if "Skill不存在" not in str(result.get("response", "")):
                    return result
            
            # 没匹配到 → chat_agent 兜底
            try:
                from core.agents.wisdom.wisdom_factory import wisdom_factory
                chat = wisdom_factory.get_agent("chat_agent", self.user_id)
                if chat:
                    return chat.process(user_input, {})
            except:
                pass
            
            return self._help()
    
    def _exec_cmd(self, cmd: str) -> Dict:
        if not self._safe(cmd):
            return self._resp(f"❌ 命令被拒绝")
        parts = shlex.split(cmd)
        if not parts or parts[0] not in self.ALLOWED_COMMANDS:
            return self._resp(f"❌ 不允许: {parts[0] if parts else cmd}")
        try:
            r = subprocess.run(cmd, shell=True, cwd=self.work_dir, capture_output=True, text=True, timeout=30)
            out = r.stdout + (f"\n[stderr]\n{r.stderr}" if r.stderr else "")
            return self._resp(f"✅ 完成\n\n{out[:2000]}" if out else "✅ 完成")
        except subprocess.TimeoutExpired:
            return self._resp("❌ 超时")
        except Exception as e:
            return self._resp(f"❌ {e}")

    def _exec_code(self, code: str) -> Dict:
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(code, {"__builtins__": __builtins__}, {})
            out = buf.getvalue()
            return self._resp(f"✅ 完成\n\n{out[:2000]}" if out else "✅ 完成")
        except Exception as e:
            return self._resp(f"❌ {e}")

    def _exec_skill(self, skill_name: str) -> Dict:
        skill_path = Path(f"skills/{skill_name}")
        if not skill_path.exists():
            return self._resp(f"这个功能暂时不可用")
        try:
            import sys
            sys.path.insert(0, str(skill_path.parent))
            module = __import__(skill_name)
            if hasattr(module, 'execute'):
                result = module.execute({})
                return self._resp(f"✅ Skill完成\n\n{json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")
            return self._resp(f"这个功能暂时不可用")
        except Exception as e:
            return self._resp(f"❌ {e}")

    def _file_op(self, op: str) -> Dict:
        parts = op.split(maxsplit=1)
        action, target = parts[0].lower(), parts[1] if len(parts) > 1 else ""
        p = self.work_dir / target if target and not target.startswith('/') else Path(target)

        if action == "read":
            return self._resp(f"📄 {p}\n\n{p.read_text()[:2000]}" if p.exists() else f"❌ 不存在: {p}")
        elif action == "write":
            content = target.split(maxsplit=1)[1] if target else ""
            (p.parent.mkdir(parents=True, exist_ok=True) if str(p) != "." else None)
            p.write_text(content)
            return self._resp(f"✅ 已写入 {p}")
        elif action == "list":
            files = list(self.work_dir.rglob("*"))[:50]
            return self._resp("📂\n" + "\n".join(str(f.relative_to(self.work_dir)) for f in files if f.is_file()))
        elif action == "delete":
            if p.exists():
                p.unlink()
                return self._resp(f"🗑 已删除 {p}")
            return self._resp(f"❌ 不存在: {p}")
        return self._resp(f"❌ 未知操作: {action}\n支持: read/write/list/delete")

    def _exec_workflow(self, name: str) -> Dict:
        try:
            from core.v5.workflow import workflow_engine
            result = workflow_engine.execute({"name": name})
            return self._resp(f"✅ 工作流完成\n\n{json.dumps(result, ensure_ascii=False, indent=2)[:2000]}")
        except Exception as e:
            return self._resp(f"❌ 工作流失败: {e}")

    def _safe(self, cmd: str) -> bool:
        import re
        return not any(re.search(p, cmd) for p in self.FORBIDDEN)

    def _help(self) -> Dict:
        return self._resp("⚡ 执行器\n\nexec 命令\ncode 代码\nskill 名称\nfile 读/写/列表/删除\nworkflow 名称")

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = ExecutorAgentV4("test")
    print(agent.process("exec ls")["response"][:200])
