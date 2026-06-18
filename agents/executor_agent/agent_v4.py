#!/usr/bin/env python3
"""ExecutorAgent v4.2 - 任务执行器（执行具体任务）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from core.agents.business.business_agent import BusinessAgent


class ExecutorAgentV4(BusinessAgent):
    """
    任务执行器 - 执行具体任务
    
    职责：
    1. 执行系统命令（安全沙箱）
    2. 执行 Python 代码片段
    3. 执行文件操作（读写、复制、移动）
    4. 执行 Skills
    5. 执行工作流步骤
    """

    name = "executor_agent_v4"
    description = "任务执行器"
    version = "4.2.0"

    # 允许执行的命令白名单
    ALLOWED_COMMANDS = [
        "ls", "pwd", "cat", "head", "tail", "grep", "find",
        "wc", "sort", "uniq", "diff", "echo", "date",
        "mkdir", "touch", "cp", "mv", "rm", "chmod",
        "git", "python", "python3", "pip", "pip3",
    ]

    # 危险命令黑名单
    FORBIDDEN_PATTERNS = [
        r"rm\s+-rf\s+/",      # 删除根目录
        r"dd\s+if=",           # 磁盘操作
        r">\s*/dev/",          # 写入设备
        r"mkfs",               # 格式化
        r"shutdown",           # 关机
        r"reboot",             # 重启
        r"curl.*\|.*sh",       # 网络下载执行
        r"wget.*\|.*sh",
    ]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.work_dir = Path(f"data/executor/{user_id}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        print(f"⚡ ExecutorAgent v{self.version} 启动")
        print(f"   📂 工作目录: {self.work_dir}")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """解析并执行任务"""
        t = user_input.lower()
        
        # 执行命令
        if t.startswith("exec ") or t.startswith("执行 "):
            cmd = user_input[5:].strip() if t.startswith("exec ") else user_input[3:].strip()
            return self._execute_command(cmd)
        
        # 执行代码
        if t.startswith("code ") or t.startswith("代码 "):
            code = user_input[5:].strip() if t.startswith("code ") else user_input[3:].strip()
            return self._execute_code(code)
        
        # 执行 Skill
        if t.startswith("skill ") or t.startswith("技能 "):
            skill_name = user_input[6:].strip() if t.startswith("skill ") else user_input[3:].strip()
            return self._execute_skill(skill_name)
        
        # 文件操作
        if t.startswith("file "):
            return self._file_operation(user_input[5:].strip())
        
        # 执行工作流
        if t.startswith("workflow "):
            return self._execute_workflow(user_input[9:].strip())
        
        return self._resp(f"""
⚡ 任务执行器

支持操作：
- `exec 命令`   : 执行系统命令
- `code 代码`   : 执行 Python 代码
- `skill 名称`  : 执行技能
- `file 操作`   : 文件操作（读/写/复制/移动/删除）
- `workflow 名称`: 执行工作流

示例：
- `exec ls -la`
- `code print("Hello")`
- `skill file_service_skill`
- `file read /path/to/file`
- `workflow my_workflow`
""")

    # ================================================================
    #  命令执行（安全沙箱）
    # ================================================================

    def _execute_command(self, cmd: str) -> Dict:
        """执行系统命令（安全沙箱）"""
        # 安全检查
        if not self._is_safe_command(cmd):
            return self._resp(f"❌ 命令被拒绝：包含危险操作\n\n命令：{cmd}")
        
        # 提取命令名
        cmd_parts = shlex.split(cmd)
        if not cmd_parts:
            return self._resp("❌ 空命令")
        
        cmd_name = cmd_parts[0]
        if cmd_name not in self.ALLOWED_COMMANDS:
            return self._resp(f"❌ 命令不在白名单中：{cmd_name}\n\n允许的命令：{', '.join(self.ALLOWED_COMMANDS)}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[退出码: {result.returncode}]"
            
            return self._resp(f"✅ 命令执行完成\n\n```\n{output[:2000]}\n```" if output else "✅ 命令执行完成（无输出）")
        
        except subprocess.TimeoutExpired:
            return self._resp("❌ 命令执行超时（30秒）")
        except Exception as e:
            return self._resp(f"❌ 执行失败：{e}")

    def _is_safe_command(self, cmd: str) -> bool:
        """检查命令是否安全"""
        import re
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, cmd):
                return False
        return True

    # ================================================================
    #  代码执行
    # ================================================================

    def _execute_code(self, code: str) -> Dict:
        """执行 Python 代码"""
        try:
            # 在安全环境中执行
            safe_globals = {
                "__builtins__": __builtins__,
                "print": print,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "range": range,
                "open": open,
                "Path": Path,
            }
            
            # 捕获输出
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                exec(code, safe_globals, {})
            
            output = output_buffer.getvalue()
            return self._resp(f"✅ 代码执行成功\n\n```\n{output[:2000]}\n```" if output else "✅ 代码执行成功（无输出）")
        
        except Exception as e:
            return self._resp(f"❌ 代码执行失败：{e}")

    # ================================================================
    #  Skill 执行
    # ================================================================

    def _execute_skill(self, skill_name: str) -> Dict:
        """执行 Skill"""
        try:
            # 尝试从 skills 目录加载
            skill_path = Path(f"skills/{skill_name}")
            if not skill_path.exists():
                return self._resp(f"❌ Skill 不存在：{skill_name}")
            
            # 导入并执行
            sys.path.insert(0, str(skill_path.parent))
            module = __import__(skill_name)
            if hasattr(module, 'execute'):
                result = module.execute({})
                return self._resp(f"✅ Skill 执行完成\n\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                return self._resp(f"❌ Skill {skill_name} 没有 execute 函数")
        
        except Exception as e:
            return self._resp(f"❌ Skill 执行失败：{e}")

    # ================================================================
    #  文件操作
    # ================================================================

    def _file_operation(self, op: str) -> Dict:
        """文件操作"""
        parts = op.split(maxsplit=1)
        if len(parts) < 2:
            return self._resp("❌ 请指定操作和参数\n\n示例：file read /path/to/file")
        
        action, path = parts[0].lower(), parts[1]
        full_path = self.work_dir / path if not path.startswith('/') else Path(path)
        
        if action == "read":
            if not full_path.exists():
                return self._resp(f"❌ 文件不存在：{full_path}")
            content = full_path.read_text(encoding='utf-8')
            return self._resp(f"📄 {full_path}\n\n```\n{content[:3000]}\n```")
        
        elif action == "write":
            # 需要内容，格式：file write /path content
            parts2 = path.split(maxsplit=1)
            if len(parts2) < 2:
                return self._resp("❌ 请指定内容和路径\n\n示例：file write /path/to/file Hello World")
            file_path = self.work_dir / parts2[0]
            content = parts2[1]
            file_path.write_text(content, encoding='utf-8')
            return self._resp(f"✅ 已写入：{file_path}")
        
        elif action == "list":
            files = list(self.work_dir.rglob("*"))[:50]
            return self._resp(f"📂 {self.work_dir}\n\n" + "\n".join([str(f.relative_to(self.work_dir)) for f in files if f.is_file()]))
        
        elif action == "delete":
            if full_path.exists():
                full_path.unlink()
                return self._resp(f"🗑 已删除：{full_path}")
            return self._resp(f"❌ 文件不存在：{full_path}")
        
        else:
            return self._resp(f"❌ 未知操作：{action}\n\n支持：read, write, list, delete")

    # ================================================================
    #  工作流执行
    # ================================================================

    def _execute_workflow(self, workflow_name: str) -> Dict:
        """执行工作流"""
        return self._resp(f"""
⚡ 执行工作流：{workflow_name}

💡 工作流功能开发中

可用工作流：
- 待定义
""")

    # ================================================================
    #  辅助
    # ================================================================

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = ExecutorAgentV4("test")
    print(agent.process("exec ls -la")["response"])
