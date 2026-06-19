#!/usr/bin/env python3
"""CodeAgent v4.2 - 乐高拼装版（保留入口 + 积木集成）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import time
from typing import Dict, Optional, Tuple, List

from core.agents.business.business_agent import BusinessAgent
from core.lib.code_repo import get_code_repo
from agents.code_agent.analyzers import analyze_code_ast, calculate_complexity
from agents.code_agent.fixers import create_fixer


class CodeAgentV4(BusinessAgent):
    """
    Code Agent - 乐高拼装版

    保留：
    - process() 直接处理入口
    - AST 分析器
    - 圈复杂度计算
    - 增量修复器
    - 代码仓库管理

    新增：
    - 语义理解（semantic_engine）
    - 推理引擎（reasoning_engine）
    - 知识检索（knowledge_engine）
    - 任务分解（task_decomposer）
    - 决策引擎（decision_engine）
    - 自愈器（self_healer）
    """

    name = "code_agent_v4"
    description = "智能代码助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        
        # ========== 项目上下文 ==========
        self._project_id: Optional[str] = None
        self._file_path: Optional[str] = None
        self._file_content: Optional[str] = None
        
        # ========== 代码仓库 ==========
        self._code_repo = get_code_repo(user_id)
        
        # ========== 专用积木（懒加载）==========
        self._task_decomposer = None
        self._decision_engine = None
        self._self_healer = None
        
        print(f"💻 CodeAgent v{self.version} 启动（乐高拼装版）")

    # ================================================================
    #  专用积木（懒加载）
    # ================================================================

    @property
    def task_decomposer(self):
        if self._task_decomposer is None:
            try:
                from core.autonomous.task_decomposer import TaskDecomposer
                self._task_decomposer = TaskDecomposer()
            except Exception as e:
                print(f"[CodeAgent] 加载任务分解器失败: {e}")
                self._task_decomposer = None
        return self._task_decomposer

    @property
    def decision_engine(self):
        if self._decision_engine is None:
            try:
                from core.autonomous.decision_engine import DecisionEngine
                self._decision_engine = DecisionEngine()
            except Exception as e:
                print(f"[CodeAgent] 加载决策引擎失败: {e}")
                self._decision_engine = None
        return self._decision_engine

    @property
    def self_healer(self):
        if self._self_healer is None:
            try:
                from core.intelligence.self_healer import SelfHealer
                self._self_healer = SelfHealer()
            except Exception as e:
                print(f"[CodeAgent] 加载自愈器失败: {e}")
                self._self_healer = None
        return self._self_healer

    # ================================================================
    #  入口
    # ================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理入口"""
        if context:
            self._project_id = context.get("project_id")
            self._file_path = context.get("file_path")
            self._file_content = context.get("file_content")
        return super().process(user_input, context)

    # ================================================================
    #  核心业务逻辑
    # ================================================================

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[CodeAgent DEBUG] context: {context}")
        """核心逻辑 - 调用积木"""
        # ========== 0. 加载用户记忆 ==========
        user_memory_text = ""
        if context and context.get("memories"):
            try:
                memories = context.get("memories", [])
                if memories:
                    memory_lines = []
                    for mem in memories[:5]:
                        if isinstance(mem, dict):
                            content_text = mem.get("content", mem.get("user_input", ""))
                            if content_text:
                                memory_lines.append(f"- {content_text}")
                        else:
                            memory_lines.append(f"- {mem}")
                    if memory_lines:
                        user_memory_text = "\n用户历史记忆:\n" + "\n".join(memory_lines)
            except Exception as e:
                print(f"[CodeAgent] 记忆提取失败: {e}")
        
        t = user_input.lower()

        # ========== 1. 感知层（通用积木）==========
        # 1.1 语义理解
        semantic_result = None
        if hasattr(self, "semantic") and self.semantic:
            try:
                semantic_result = self.semantic.understand(user_input)
            except Exception as e:
                print(f"[CodeAgent] 语义理解失败: {e}")

        # 1.2 情感感知
        emotion_result = {}
        if hasattr(self, "emotion") and self.emotion:
            try:
                emotion_result = self.emotion.analyze(user_input)
            except Exception as e:
                print(f"[CodeAgent] 情感分析失败: {e}")

        # 1.3 推理增强（如果是复杂推理任务）
        reasoning_result = None
        if hasattr(self, "reasoning") and self.reasoning and any(kw in t for kw in ["为什么", "怎么", "如何", "如果", "那么"]):
            try:
                reasoning_result = self.reasoning.process(user_input)
            except Exception as e:
                print(f"[CodeAgent] 推理失败: {e}")

        # ========== 2. 知识检索 ==========
        knowledge_result = None
        if hasattr(self, "knowledge") and self.knowledge:
            try:
                knowledge_result = self.knowledge.query(user_input)
            except Exception as e:
                print(f"[CodeAgent] 知识检索失败: {e}")

        # ========== 3. 任务路由 ==========
        # 3.1 判断任务类型
        if any(kw in t for kw in ["分析", "检查", "审查", "review"]):
            return self._handle_analyze(user_input)
        
        if any(kw in t for kw in ["修复", "fix", "改正"]):
            return self._handle_fix(user_input)
        
        if any(kw in t for kw in ["生成", "写", "create", "实现"]):
            return self._handle_generate(user_input)
        
        if any(kw in t for kw in ["解释", "说明", "explain"]):
            return self._handle_explain(user_input)

        # 3.2 复杂任务：分解 + 决策
        if hasattr(self, "task_decomposer") and self.task_decomposer and self._is_complex(user_input):
            try:
                decomposed = self.task_decomposer.decompose(user_input)
                return self._handle_decomposed(decomposed)
            except Exception as e:
                print(f"[CodeAgent] 任务分解失败: {e}")

        # 3.3 项目/文件操作
        if any(kw in t for kw in ["添加项目", "导入项目", "列出项目"]):
            return self._handle_project(user_input)
        
        if any(kw in t for kw in ["读取文件", "打开文件"]):
            return self._handle_file(user_input)
        # 3.4 记忆/名字查询
        if any(kw in t for kw in ["名字", "姓名", "叫什么", "我是谁", "我的名字"]):
            return self._handle_memory_query(user_input, context)

        # 3.5 默认：对话
        return self._handle_chat(user_input)

    # ================================================================
    #  分析（AST + 圈复杂度）
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

    # ================================================================
    #  修复（增量修复器）
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
        return self._resp(f"## 🔧 修复完成\n\n修复 {fixed}/{len(issues)} 个问题。\n\n```python\n{fixed_code}\n```")

    # ================================================================
    #  生成
    # ================================================================

    def _handle_generate(self, user_input: str) -> Dict:
        prompt = f"生成代码，只输出代码：{user_input}"
        code = self._call_llm(prompt)
        if not code:
            return self._resp("⚠️ 生成失败，请重试。")
        return self._resp(f"```python\n{code}\n```")

    # ================================================================
    #  解释
    # ================================================================

    def _handle_explain(self, user_input: str) -> Dict:
        code = self._extract_code(user_input)
        if not code:
            return self._resp("请提供要解释的代码。")
        prompt = f"用简单语言解释这段代码：\n```python\n{code[:2000]}\n```"
        explanation = self._call_llm(prompt)
        return self._resp(f"## 📖 代码解释\n\n{explanation or '解释生成失败。'}")

    # ================================================================
    #  分解任务处理
    # ================================================================

    def _handle_decomposed(self, decomposed: Dict) -> Dict:
        sub_tasks = decomposed.get("sub_tasks", [])
        if not sub_tasks:
            return self._resp("任务分解失败。")
        
        results = []
        for task in sub_tasks:
            desc = task.get("description", "")
            action = task.get("action", "process")
            if action == "analyze":
                results.append(self._handle_analyze(desc))
            elif action == "generate":
                results.append(self._handle_generate(desc))
            else:
                results.append(self._handle_chat(desc))
        
        output = "## 📋 任务执行结果\n\n"
        for i, r in enumerate(results, 1):
            output += f"### 子任务 {i}\n{r.get('response', '完成')}\n\n"
        return self._resp(output)

    # ================================================================
    #  项目管理
    # ================================================================

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

    # ================================================================
    #  文件操作
    # ================================================================

    def _handle_file(self, user_input: str) -> Dict:
        match = re.search(r'(?:读取文件|打开文件)[：:]?\s*(\S+)', user_input)
        if not match:
            return self._resp("请提供文件名。示例：读取文件 main.py")
        
        file_path = match.group(1)
        content = self._read_file(file_path)
        if content:
            preview = content[:500] + ("..." if len(content) > 500 else "")
            return self._resp(f"📄 **{file_path}**\n\n```\n{preview}\n```")
        return self._resp(f"未找到文件: {file_path}")
    
    # ================================================================
    #  记忆查询（名字/身份）
    # ================================================================

    def _handle_memory_query(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理名字/身份查询，从记忆中获取"""
        try:
            # 从 context 中获取记忆
            memories = context.get("memories", []) if context else []

            # 在记忆中搜索名字
            for mem in memories:
                if isinstance(mem, dict):
                    content_text = mem.get("content", mem.get("user_input", ""))
                    if "名字" in content_text or "姓名" in content_text:
                        import re
                        match = re.search(r'(?:名字|姓名)[：:]\s*(\S+)', content_text)
                        if match:
                            name = match.group(1)
                            return self._resp(f"您的名字是：{name}")
                elif isinstance(mem, str):
                    if "名字" in mem or "姓名" in mem:
                        import re
                        match = re.search(r'(?:名字|姓名)[：:]\s*(\S+)', mem)
                        if match:
                            name = match.group(1)
                            return self._resp(f"您的名字是：{name}")

            # 检查用户输入中是否包含名字信息
            import re
            name_match = re.search(r'(?:我叫|叫我|名字是)[：:]\s*(\S+)', user_input)
            if name_match:
                name = name_match.group(1)
                return self._resp(f"您的名字是：{name}")

            return self._resp("我暂时没有您名字的记忆，请告诉我您的名字。")
        except Exception as e:
            print(f"[CodeAgent] 记忆查询失败: {e}")
            return self._resp("我暂时无法获取您的名字信息。")


    # ================================================================
    #  对话
    # ================================================================

    def _handle_chat(self, user_input: str) -> Dict:
        prompt = f"你是代码助手，简短回复：{user_input}"
        response = self._call_llm(prompt)
        return self._resp(response or "我没理解，能再说一遍吗？")

    # ================================================================
    #  辅助方法
    # ================================================================
    def _extract_code(self, text: str) -> Optional[str]:
        """提取代码（增强版）"""
        # 1. 标准代码块
        match = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
        # 2. 多行代码特征
        if "\n" in text:
            if any(kw in text for kw in ["def ", "class ", "import ", "from ", "print(", "return "]):
                # 去掉中文前缀
                lines = text.split('\n')
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith(('解释', '分析', '代码'))]
                if code_lines:
                    return '\n'.join(code_lines)
    
        # 3. 单行代码
        if "print(" in text or "=" in text or "lambda" in text or "return" in text:
            # 提取可能是代码的部分
            code_match = re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(].+', text)
            if code_match:
                return code_match.group(0)
    
        return None
    
    def _read_file(self, file_path: str) -> Optional[str]:
        projects = self._code_repo.list_projects()
        if projects:
            return self._code_repo.get_file_content(projects[0]["id"], file_path)
        return None

    def _is_complex(self, user_input: str) -> bool:
        indicators = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后"]
        return len(user_input) > 50 and any(ind in user_input for ind in indicators)

    def _format_issues(self, issues: List[Dict]) -> str:
        lines = [f"## 📊 分析结果\n", f"共发现 {len(issues)} 个问题：\n"]
        for i in issues:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(i.get("severity", "low"), "⚪")
            lines.append(f"{emoji} **L{i.get('line', '?')}**: {i.get('description', '')}")
        lines.append("\n💡 输入「修复」自动修复这些问题")
        return "\n".join(lines)

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 200}
                },
                timeout=120
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[CodeAgent] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)


if __name__ == "__main__":
    agent = CodeAgentV4("test")
    print(agent.process("写一个排序函数")["response"])

 
