#!/usr/bin/env python3
"""CodeAgent v4.2 - 精简稳定版（保留 AST + 增量修复）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
import time
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any

from core.agents.business.business_agent import BusinessAgent
from core.lib.code_repo import get_code_repo
from agents.code_agent.analyzers import analyze_code_ast, calculate_complexity
from agents.code_agent.fixers import create_fixer


class CodeAgentV4(BusinessAgent):
    """代码 Agent - 精简稳定版"""

    name = "code_agent_v4"
    description = "智能代码助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._code_repo = get_code_repo(user_id)
        self._project_id: Optional[str] = None
        self._file_path: Optional[str] = None
        
        # LLM 配置
        self._llm_model = "qwen2.5:7b"
        self._llm_timeout = 60
        self._max_retries = 2
        
        print(f"💻 CodeAgent v{self.version} 启动")

    # ================================================================
    #  核心入口
    # ================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context:
            self._project_id = context.get("project_id")
            self._file_path = context.get("file_path")
        return self._handle(user_input)

    def _handle(self, user_input: str) -> Dict:
        """核心处理"""
        intent = self._detect_intent(user_input)
        
        handlers = {
            "analyze": self._handle_analyze,
            "fix": self._handle_fix,
            "generate": self._handle_generate,
            "explain": self._handle_explain,
            "review": self._handle_review,
            "project": self._handle_project,
            "file": self._handle_file,
        }
        
        handler = handlers.get(intent, self._handle_chat)
        return handler(user_input)

    # ================================================================
    #  意图检测
    # ================================================================

    def _detect_intent(self, text: str) -> str:
        """检测用户意图"""
        t = text.lower()
        
        if any(kw in t for kw in ["添加项目", "导入项目", "列出项目", "我的项目"]):
            return "project"
        if any(kw in t for kw in ["读取文件", "打开文件"]):
            return "file"
        if any(kw in t for kw in ["分析", "检查", "审查", "review"]):
            return "review" if "深度" in t else "analyze"
        if any(kw in t for kw in ["修复", "fix", "改正", "纠正"]):
            return "fix"
        if any(kw in t for kw in ["生成", "写", "create", "实现"]):
            return "generate"
        if any(kw in t for kw in ["解释", "说明", "explain"]):
            return "explain"
        
        return "chat"

    # ================================================================
    #  分析（AST 静态分析）
    # ================================================================

    def _handle_analyze(self, user_input: str) -> Dict:
        code = self._extract_code(user_input)
        if not code and self._file_path:
            code = self._read_file(self._file_path)
        
        if not code:
            return self._resp("请提供要分析的代码。")
        
        # AST 分析
        ast_issues = analyze_code_ast(code, self._file_path or "")
        complexity_issues = calculate_complexity(code)
        
        all_issues = ast_issues + complexity_issues
        all_issues.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3))
        
        if not all_issues:
            return self._resp("✅ 代码质量良好，未发现明显问题。")
        
        return self._resp(self._format_issues(all_issues))

    def _format_issues(self, issues: List[Dict]) -> str:
        lines = [f"## 📊 分析结果", "", f"共发现 {len(issues)} 个问题：", ""]
        for i in issues:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(i.get("severity", "low"), "⚪")
            lines.append(f"{emoji} **L{i.get('line', '?')}**: {i.get('description', '')}")
        lines.append("")
        lines.append("💡 输入「修复」自动修复这些问题")
        return "\n".join(lines)

    # ================================================================
    #  修复（增量修复）
    # ================================================================

    def _handle_fix(self, user_input: str) -> Dict:
        code = self._extract_code(user_input)
        if not code and self._file_path:
            code = self._read_file(self._file_path)
        
        if not code:
            return self._resp("请提供要修复的代码。")
        
        issues = analyze_code_ast(code, self._file_path or "")
        
        if not issues:
            return self._resp("✅ 代码没有发现问题，无需修复。")
        
        # 逐行修复
        lines = code.split("\n")
        fixed = 0
        
        for issue in issues:
            line_num = issue.get("line")
            if line_num and 1 <= line_num <= len(lines):
                desc = issue.get("description", "")
                if "缺少文档字符串" in desc:
                    indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
                    lines[line_num - 1] += '\n' + ' ' * indent + '"""文档字符串"""'
                    fixed += 1
        
        fixed_code = "\n".join(lines)
        
        return self._resp(f"""
## 🔧 修复完成

修复 {fixed}/{len(issues)} 个问题。

```python
{fixed_code}
💡 保存文件以应用修改。
"""     )
    #================================================================
    #生成
    #================================================================
    def _handle_generate(self, user_input: str) -> Dict:
        prompt = f"生成代码，只输出代码：{user_input}"
        code = self._call_llm(prompt)

        if not code:
            return self._resp("⚠️ 生成失败，请重试。")

        return self._resp(f"python\n{code}\n")

    #================================================================
    #解释
    #================================================================
    def _handle_explain(self, user_input: str) -> Dict:
        code = self._extract_code(user_input)
        if not code:
            return self._resp("请提供要解释的代码。")

        prompt = f"用简单语言解释这段代码：\npython\n{code[:2000]}\n"
        explanation = self._call_llm(prompt)

        return self._resp(f"## 📖 代码解释\n\n{explanation or '解释生成失败。'}")

    #================================================================
    #深度审查
    #================================================================
    def _handle_review(self, user_input: str) -> Dict:
        code = self._extract_code(user_input)
        if not code and self._file_path:
            code = self._read_file(self._file_path)

        if not code:
            return self._resp("请提供要审查的代码。")

        #静态分析
        ast_issues = analyze_code_ast(code, self._file_path or "")
        complexity_issues = calculate_complexity(code)
        all_issues = ast_issues + complexity_issues

        #LLM 深度分析
        prompt = f"""深度审查以下代码，给出改进建议：

```python
{code[:2000]}
```"""
        llm_review = self._call_llm(prompt)

        result = f"## 📊 深度审查报告\n\n"
        if all_issues:
            result += self._format_issues(all_issues) + "\n\n"
        if llm_review:
            result += f"### 🤖 建议\n\n{llm_review}"
        else:
            result += "✅ 代码结构合理。"

        return self._resp(result)

    #================================================================
    #项目管理
    #================================================================
    def _handle_project(self, user_input: str) -> Dict:
        t = user_input.lower()

        if "添加" in t or "导入" in t:
            match = re.search(r'(?:添加项目|导入项目)[：:]?\s*(.+)', user_input)
            if match:
                path = match.group(1).strip()
                result = self._code_repo.add_project(path)
                if result.get("success"):
                    return self._resp(f"✅ 已添加项目: {result.get('name')}\n📁 {result.get('file_count')} 个文件")
                return self._resp(f"❌ 添加失败: {result.get('error')}")
            return self._resp("请提供项目路径。示例：添加项目 /path/to/project")

        projects = self._code_repo.list_projects()
        if not projects:
            return self._resp("还没有添加项目。使用「添加项目 /路径」")

        lines = ["📁 我的项目"]
        for p in projects:
            lines.append(f"  • {p.get('name')} - {p.get('file_count')} 个文件")
        return self._resp("\n".join(lines))
    #================================================================
    #文件操作
    #================================================================
    def _handle_file(self, user_input: str) -> Dict:
        match = re.search(r'(?:读取文件|打开文件)[：:]?\s*(\S+)', user_input)
        if not match:
            return self._resp("请提供文件名。示例：读取文件 main.py")

        file_path = match.group(1)
        content = self._read_file(file_path)
        if content:
            preview = content[:500] + ("..." if len(content) > 500 else "")
            return self._resp(f"📄 {file_path}\n\n\n{preview}\n")
        return self._resp(f"未找到文件: {file_path}")

    def _read_file(self, file_path: str) -> Optional[str]:
        projects = self._code_repo.list_projects()
        if projects:
            return self._code_repo.get_file_content(projects[0]["id"], file_path)
        return None

    #================================================================
    #通用对话
    #================================================================
    def _handle_chat(self, user_input: str) -> Dict:
        prompt = f"你是代码助手，简短回复：{user_input}"
        response = self._call_llm(prompt)
        return self._resp(response or "我没理解，能再说一遍吗？")

    #================================================================
    #辅助方法
    #================================================================
    def _extract_code(self, text: str) -> Optional[str]:
        match = re.search(r'(?:python)?\s*\n(.*?)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        if "\n" in text and ("def " in text or "class " in text or "import " in text):
            return text
        return None

    def _call_llm(self, prompt: str) -> Optional[str]:
        for attempt in range(self._max_retries):
            try:
                import requests
                resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self._llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 500}
                    },
                    timeout=self._llm_timeout
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "").strip()
            except Exception as e:
                print(f"[CodeAgent] 尝试 {attempt+1} 失败: {e}")
                time.sleep(0.5 * (attempt + 1))
        return None

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)


if __name__ == "__main__":
    agent = CodeAgentV4("test")
    print(agent.process("写一个排序函数")["response"])
