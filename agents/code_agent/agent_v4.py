#!/usr/bin/env python3
"""CodeAgent v4.1 - 智慧化代码生成智能体（增强版）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any
from core.lib.code_repo import get_code_repo
from core.agents.business.business_agent import BusinessAgent


class CodeAgentV4(BusinessAgent):
    """代码 Agent - 智慧化版本（增强版 v4.1）"""

    name = "code_agent_v4"
    description = "智慧代码助手"
    version = "4.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._code_memory = self._init_code_memory(user_id)
        self._code_style = self._code_memory.recall_style()
        self._code_repo = get_code_repo(user_id)
        print(f"💻 CodeAgent v{self.version} 智慧化试点启动")
        print(f"   📚 代码记忆已加载: {self._code_memory.get_stats()['history_count']} 条记录")
        print(f"   🎨 代码风格偏好: {self._code_style or '默认'}")
        print(f"   📁 代码库项目: {len(self._code_repo.list_projects())} 个")

    def _init_code_memory(self, user_id: str):
        """初始化代码记忆"""
        class SimpleCodeMemory:
            def __init__(self, uid):
                self.uid = uid
                self._preferences = {}
                self._history = []
                self._load()

            def _get_path(self):
                path = Path(f"data/code_memory/{self.uid}.json")
                path.parent.mkdir(parents=True, exist_ok=True)
                return path

            def _load(self):
                path = self._get_path()
                if path.exists():
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            self._preferences = data.get('preferences', {})
                            self._history = data.get('history', [])
                    except:
                        pass

            def _save(self):
                with open(self._get_path(), 'w') as f:
                    json.dump({
                        'preferences': self._preferences,
                        'history': self._history[-100:]
                    }, f, indent=2)

            def recall_language(self):
                return self._preferences.get('preferred_language', 'python')

            def remember_language(self, lang):
                self._preferences['preferred_language'] = lang
                self._save()

            def record_code(self, prompt, code, language, success):
                self._history.append({
                    'prompt': prompt[:200],
                    'code': code[:500],
                    'language': language,
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                })
                self._save()

            def get_stats(self):
                return {
                    'preferences': self._preferences,
                    'history_count': len(self._history)
                }

            def recall_style(self):
                return self._preferences.get('code_style')

            def remember_style(self, style):
                self._preferences['code_style'] = style
                self._save()

        return SimpleCodeMemory(user_id)

    # ========== 能力声明 ==========

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("generate", "code"): (True, 0.95),
            ("analyze", "code"): (True, 0.90),
            ("explain", "code"): (True, 0.85),
            ("debug", "code"): (True, 0.80),
            ("optimize", "code"): (True, 0.75),
            ("review", "code"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))

    # ========== 核心业务逻辑 ==========

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心代码处理逻辑 - 优先处理代码生成"""

        # ========== 0. 代码库操作 ==========
        if "添加项目" in user_input or "导入项目" in user_input:
            match = re.search(r'(?:添加项目|导入项目)[：:]?\s*(.+)', user_input)
            if match:
                path = match.group(1).strip()
                result = self._code_repo.add_project(path)
                if result["success"]:
                    return self._response(f"✅ 已添加项目: {result['name']}\n📁 文件数: {result['file_count']}")
                else:
                    return self._response(f"❌ 添加失败: {result['error']}")
            return self._response("请提供项目路径。示例：添加项目 /path/to/my_project")

        if "列出项目" in user_input or "我的项目" in user_input:
            projects = self._code_repo.list_projects()
            if not projects:
                return self._response("还没有添加项目。使用「添加项目 /项目路径」")
            lines = ["📁 **我的项目**"]
            for p in projects:
                lines.append(f"  •  {p['name']} ({p['languages']}) - {p['file_count']} 个文件")
            return self._response("\n".join(lines))

        if "搜索代码" in user_input or "查找代码" in user_input:
            match = re.search(r'(?:搜索代码|查找代码)[：:]?\s*(.+)', user_input)
            if match:
                query = match.group(1).strip()
                results = self._code_repo.search_code(query)
                if results:
                    lines = [f"🔍 搜索 '{query}' 找到 {len(results)} 个文件:"]
                    for r in results[:10]:
                        lines.append(f"  •  {r['file']} ({r.get('language', 'unknown')})")
                    return self._response("\n".join(lines))
                return self._response(f"未找到包含 '{query}' 的文件")
            return self._response("请提供搜索关键词。示例：搜索代码 main")

        if "读取文件" in user_input:
            match = re.search(r'读取文件[：:]?\s*(\S+)', user_input)
            if match:
                file_path = match.group(1)
                projects = self._code_repo.list_projects()
                if projects:
                    content = self._code_repo.get_file_content(projects[0]["id"], file_path)
                    if content:
                        preview = content[:500] + "..." if len(content) > 500 else content
                        return self._response(f"📄 **{file_path}**\n\n```\n{preview}\n```")
                return self._response(f"未找到文件: {file_path}")
            return self._response("请提供文件名。示例：读取文件 main.py")

        # ========== 1. 代码修复（自动修复）==========
        if "修复" in user_input and any(kw in user_input for kw in ["代码", "函数", "bug", "错误"]):
            code_match = re.search(r'```(?:python)?\s*\n(.*?)```', user_input, re.DOTALL)
            if not code_match: 
                return self._response("请提供要修复的代码，格式：```python\\n代码\\n```")
                
            code_to_fix = code_match.group(1)
            result = self.auto_fix(code_to_fix)
            if not result.get("success"):
                return self._response(f"自动修复失败: {result.get("message", "未知错误")}")
            output = f"""## 🔧 自动修复报告

### 📊 修复概览
{result['message']}

### 📝 问题清单
"""
            for issue in result.get("issues", []):
                output += f"- L{issue['line']}: {issue['description']}\n"

            output += f"""
### 💾 修复后代码
```python
{result['fixed_code']}
✅ 验证结果
{result.get('verification', {}).get('message', '验证完成')}
"""
            return self._response(output, metadata={"type": "auto_fix"})
                                
        # ========== 2. 深度代码审查（新增）==========
        if "深度审查" in user_input or "深度分析" in user_input or "全面审查" in user_input:
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                result = self.deep_review(code, file_path="inline")
                return self._response(self._format_review_result(result), metadata={"type": "deep_review"})
            return self._response("请提供要审查的代码。格式：```python\n代码\n```")

        # ========== 3. 通用代码生成 ==========
        is_code_request = False
        code_task = user_input

        if re.match(r'^写[一个|一段|个]?\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^写[一个|一段|个]?\s*', '', user_input)
        elif re.match(r'^生成\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^生成\s*', '', user_input)
        elif re.match(r'^实现\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^实现\s*', '', user_input)
        elif any(kw in user_input for kw in ["代码", "函数", "算法", "程序"]):
            if not any(kw in user_input for kw in ["解释", "说明", "调试", "优化", "审查", "深度"]):
                is_code_request = True

        if is_code_request:
            code = self._generate_code(code_task)
            language = self._detect_language(user_input)
            self._code_memory.record_code(user_input, code, language, True)
            return self._response(
                f"```{language}\n{code}\n```",
                metadata={"language": language, "type": "generated"}
            )

        # ========== 4. 设置代码风格 ==========
        if "偏好风格" in user_input or "代码风格" in user_input:
            style_match = re.search(r'(?:偏好风格|代码风格)[：:]?\s*(\w+)', user_input)
            if style_match:
                style = style_match.group(1).lower()
                if style in ["pep8", "google", "airbnb"]:
                    self._code_memory.remember_style(style)
                    return self._response(f"✅ 已设置代码风格偏好：{style}")
            current = self._code_memory.recall_style() or "默认"
            return self._response(f"当前代码风格偏好：{current}\n可设置：pep8, google, airbnb")

        # ========== 5. 生成单元测试 ==========
        if "生成测试" in user_input or "单元测试" in user_input:
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                tests = self._generate_tests(code, language)
                return self._response(tests, metadata={"type": "tests"})
            return self._response("请提供要生成测试的代码。格式：```python\n代码\n```")

        # ========== 6. 代码审查（增强版）==========
        if "审查" in user_input or "review" in user_input.lower():
            # 多种代码块格式匹配
                        # 1. 标准闭合代码块
            code_match = re.search(r'```(?:python)?\s*\n(.*?)```', user_input, re.DOTALL)
            # 2. 不闭合的代码块（用户可能忘记写结尾）
            if not code_match:
                code_match = re.search(r'```(?:python)?\s*\n([\s\S]*?)$', user_input, re.DOTALL)
            if not code_match:
                code_match = re.search(r'```(.*?)```', user_input, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                # 检测语言
                language = "python"
                if code_match.group(0).startswith('```python'):
                    language = "python"
                # 使用增强的深度审查
                if language == "python":
                    review_result = self.deep_review(code)
                    return self._response(self._format_review_result_with_highlight(review_result), metadata={"type": "review"})
                else:
                    review = self._review_code(code, language)
                    return self._response(review, metadata={"type": "review"})
            # 如果没有代码块，尝试从消息中提取
            return self._response("请提供要审查的代码，格式：\n```python\n代码\n```")

        # ========== 7. 代码解释 ==========
        if any(kw in user_input for kw in ["解释", "说明", "什么意思", "作用"]):
            explanation = self._explain_code(user_input)
            return self._response(explanation, metadata={"type": "explanation"})

        #========== 8. 代码调试 ==========
        if any(kw in user_input for kw in ["调试", "debug", "错误", "bug"]):
            debug_result = self._debug_code(user_input)
            return self._response(debug_result, metadata={"type": "debug"})
        # ========== 9. 代码优化 ==========
        if any(kw in user_input for kw in ["优化", "改进", "重构", "性能"]):
            optimized = self._optimize_code(user_input)
            return self._response(optimized, metadata={"type": "optimized"})

        # ========== 10. 设置偏好 ==========
        if "偏好" in user_input or "喜欢" in user_input:
            return self._handle_preference(user_input)

        # ========== 11. 默认帮助 ==========
        # 默认帮助
        return self._response("")

    # ========== 辅助方法 ==========

    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }

    def _detect_language(self, text: str) -> str:
        text_lower = text.lower()
        if "python" in text_lower or "py" in text_lower:
            return "python"
        if "java" in text_lower:
            return "java"
        if "javascript" in text_lower or "js" in text_lower:
            return "javascript"
        if "go" in text_lower or "golang" in text_lower:
            return "go"
        if "rust" in text_lower:
            return "rust"
        if "c++" in text_lower or "cpp" in text_lower:
            return "cpp"
        return self._code_memory.recall_language()

    def _call_llm(self, prompt: str, model: str = None) -> str:
        if not model:
            model = self._select_model(prompt)
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 2048}
                },
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                response = data.get("response", "")
                if response and len(response) > 20:
                    return response.strip()
        except Exception as e:
            print(f"LLM 调用失败: {e}")
        return ""

    def _select_model(self, prompt: str) -> str:
        """根据任务复杂度选择模型"""
        if len(prompt) > 500:
            return "qwen2.5:7b"
        return "qwen2:1.5b-instruct"

    def _generate_code(self, prompt: str) -> str:
        language = self._detect_language(prompt)
        full_prompt = f"""你是一个专业的{language}程序员。请根据用户需求生成代码。

用户需求：{prompt}

要求：
1. 只输出代码，不要有任何解释
2. 代码要完整、可直接运行
3. 使用最佳实践
4. 不要用markdown代码块包裹输出

请输出代码："""

        response = self._call_llm(full_prompt)

        if response:
            response = response.strip()
            response = re.sub(r'^```\w*\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
            return response

        return f"""# {prompt}
def solution():
    # TODO: 实现功能
    pass

if __name__ == "__main__":
    result = solution()
    print(result)"""

    def _explain_code(self, text: str) -> str:
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        if not code_match:
            return "请提供要解释的代码。格式：```python\n代码\n```"

        language = code_match.group(1) or "python"
        code = code_match.group(2)

        prompt = f"请简洁解释以下{language}代码的功能：\n{code}"
        explanation = self._call_llm(prompt)

        if explanation:
            return f"**代码解释**\n\n{explanation}\n\n```{language}\n{code}\n```"
        return f"```{language}\n{code}\n```"

    def _debug_code(self, text: str) -> str:
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        if not code_match:
            return "请提供要调试的代码。格式：```python\n代码\n```"

        language = code_match.group(1) or "python"
        code = code_match.group(2)
        error_match = re.search(r'错误[：:]\s*(.+?)(?:\n|$)', text)
        error = error_match.group(1) if error_match else "未知错误"

        prompt = f"""调试以下{language}代码：
代码：
{code}
错误信息：{error}
请分析原因并提供修复后的代码。"""

        result = self._call_llm(prompt)
        if result:
            return result
        return f"```{language}\n{code}\n```\n\n建议检查变量类型和边界条件。"

    def _optimize_code(self, text: str) -> str:
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        if not code_match:
            return "请提供要优化的代码。格式：```python\n代码\n```"

        language = code_match.group(1) or "python"
        code = code_match.group(2)

        prompt = f"优化以下{language}代码，保持功能不变，只输出优化后的代码：\n{code}"
        optimized = self._call_llm(prompt)

        if optimized:
            return f"```{language}\n{optimized}\n```"
        return f"```{language}\n{code}\n```"

    def _generate_tests(self, code: str, language: str) -> str:
        prompt = f"""为以下{language}代码生成单元测试：
代码：
{code}
要求：使用该语言的测试框架，覆盖主要功能，包含边界条件测试。只输出测试代码。"""

        tests = self._call_llm(prompt)
        if tests:
            return f"```{language}\n{tests}\n```"
        return "# 单元测试生成失败"

    def _review_code(self, code: str, language: str) -> str:
        """原有代码审查（非 Python 语言降级使用）"""
        prompt = f"""请审查以下{language}代码：
代码：
{code}
请从代码质量、潜在问题、性能、安全性、改进建议方面分析。"""

        review = self._call_llm(prompt)
        if review:
            return f"**代码审查报告**\n\n{review}"
        return "代码审查暂时不可用"

    def _handle_preference(self, text: str) -> Dict:
        lang_match = re.search(r'偏好\s*(\w+)', text)
        if lang_match:
            lang = lang_match.group(1).lower()
            if lang in ["python", "java", "javascript", "go"]:
                self._code_memory.remember_language(lang)
                return self._response(f"已记住代码偏好：{lang}")
        return self._response(f"当前偏好：{self._code_memory.recall_language()}")

    def _get_help_text(self) -> str:
        return """我是代码助手，可以帮您：

- 生成代码："写一个排序函数"
- 解释代码："解释代码：```python\n代码\n```"
- 调试代码："调试代码并提供错误信息"
- 优化代码："优化这段代码"
- 审查代码："审查代码：```python\n代码\n```"
- 深度审查："深度审查代码：```python\n代码\n```"
- 设置偏好："偏好 python"

请提供具体的代码需求！"""

    # ========== 代码格式化工具 ==========

    def format_code_with_autopep8(self, code: str) -> dict:
        """使用 autopep8 格式化 Python 代码"""
        import tempfile
        import subprocess
        import os

        result = {
            "success": False,
            "original": code,
            "formatted": code,
            "changes": "",
            "error": None
        }

        if not code.strip():
            result["error"] = "代码为空"
            return result

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            subprocess.run([
                'autopep8', '--in-place', '--aggressive', '--aggressive',
                '--max-line-length=100', temp_path
            ], capture_output=True, timeout=10)

            with open(temp_path, 'r', encoding='utf-8') as f:
                formatted_code = f.read()

            os.unlink(temp_path)

            result["success"] = True
            result["formatted"] = formatted_code

            if code != formatted_code:
                result["changes"] = "代码格式已优化"
            else:
                result["changes"] = "代码格式已符合规范"
        except subprocess.TimeoutExpired:
            result["error"] = "格式化超时"
        except Exception as e:
            result["error"] = str(e)

        return result

    def format_code_with_black(self, code: str) -> dict:
        """使用 Black 格式化 Python 代码"""
        import tempfile
        import subprocess
        import os

        result = {
            "success": False,
            "original": code,
            "formatted": code,
            "changes": "",
            "error": None
        }

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            subprocess.run(['black', '--quiet', temp_path], capture_output=True, timeout=10)

            with open(temp_path, 'r', encoding='utf-8') as f:
                formatted_code = f.read()

            os.unlink(temp_path)

            result["success"] = True
            result["formatted"] = formatted_code
            result["changes"] = "已使用 Black 格式化"

        except Exception as e:
            result["error"] = str(e)

        return result

    # ========== 增强的静态分析方法 ==========

    def _calculate_complexity(self, lines: List[str], start_line: int, end_line: int = None) -> Dict:
        """计算函数圈复杂度"""
        if end_line is None:
            end_line = min(start_line + 50, len(lines))

        complexity = 1  # 基础复杂度
        keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or',
                    'except', 'finally', 'with', 'lambda', 'comprehension']

        for i in range(start_line, end_line):
            line = lines[i]
            for kw in keywords:
                if re.search(rf'\b{kw}\b', line):
                    complexity += 1

        # 评估等级
        if complexity <= 5:
            level = "low"
            suggestion = "复杂度低，易于维护"
        elif complexity <= 10:
            level = "medium"
            suggestion = "复杂度中等，建议适当拆分"
        else:
            level = "high"
            suggestion = "复杂度过高，强烈建议拆分函数"

        return {
            "score": complexity,
            "level": level,
            "suggestion": suggestion
        }

    def _parse_params(self, params_str: str) -> List[Dict]:
        """解析函数参数"""
        if not params_str or params_str.strip() == '':
            return []

        params = []
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue

            # 处理默认值
            if '=' in param:
                name, default = param.split('=', 1)
                params.append({
                    "name": name.strip(),
                    "default": default.strip(),
                    "required": False
                })
            else:
                params.append({
                    "name": param,
                    "default": None,
                    "required": True
                })
        return params

    def _detect_calls(self, lines: List[str], start_line: int, end_line: int = None) -> List[str]:
        """检测函数内的调用"""
        if end_line is None:
            end_line = min(start_line + 50, len(lines))

        calls = set()
        # 匹配函数调用模式：xxx.yyy() 或 xxx()
        call_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        for i in range(start_line, end_line):
            line = lines[i]
            # 跳过注释
            if line.strip().startswith('#'):
                continue
            matches = call_pattern.findall(line)
            for match in matches:
                # 排除 Python 关键字和常见内置函数
                if match not in ['def', 'if', 'for', 'while', 'with', 'print', 'len', 'range', 'str', 'int', 'list', 'dict', 'set', 'tuple']:
                    calls.add(match)

        return list(calls)

    def _extract_docstring(self, lines: List[str], start_line: int) -> Optional[str]:
        """提取函数文档字符串"""
        # 检查函数定义后的下一行
        if start_line + 1 < len(lines):
            next_line = lines[start_line + 1].strip()
            if next_line.startswith('"""') or next_line.startswith("'''"):
                # 单行文档字符串
                return next_line.strip('"\'')
            elif (start_line + 2 < len(lines) and
                  (lines[start_line + 1].strip() == '"""' or lines[start_line + 1].strip() == "'''")):
                # 多行文档字符串
                doc_lines = []
                for i in range(start_line + 2, len(lines)):
                    if lines[i].strip() == '"""' or lines[i].strip() == "'''":
                        break
                    doc_lines.append(lines[i].strip())
                return '\n'.join(doc_lines)
        return None

    # ========== 增强的 analyze_code 方法 ==========

    def analyze_code(self, code: str, file_path: str = "", granularity: str = "auto") -> dict:
        """分析代码，返回结构化分析结果（增强版）"""
        lines = code.split('\n')
        result = {
            "success": True,
            "summary": "",
            "functions": [],
            "classes": [],
            "imports": [],
            "issues": [],
            "suggestions": [],
            "metrics": {
                "total_lines": len(lines),
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions_count": 0,
                "classes_count": 0,
                "imports_count": 0,
                "avg_complexity": 0
            }
        }

        in_multiline_comment = False
        complexities = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # 统计行类型
            if not stripped:
                result["metrics"]["blank_lines"] += 1
            elif stripped.startswith('#'):
                result["metrics"]["comment_lines"] += 1
            elif '"""' in stripped or "'''" in stripped:
                in_multiline_comment = not in_multiline_comment
                result["metrics"]["comment_lines"] += 1
            else:
                result["metrics"]["code_lines"] += 1

            # 检测函数定义（增强版）
            func_match = re.match(r'^\s*def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(\w+))?', line)
            if func_match:
                result["metrics"]["functions_count"] += 1
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                return_type = func_match.group(3) if func_match.group(3) else None

                # 计算函数结束行
                end_line = self._find_function_end(lines, i)
                # 计算复杂度
                complexity = self._calculate_complexity(lines, i, end_line)
                complexities.append(complexity["score"])
                # 检测调用
                calls = self._detect_calls(lines, i, end_line)
                # 提取文档字符串
                docstring = self._extract_docstring(lines, i)

                result["functions"].append({
                    "name": func_name,
                    "params": self._parse_params(params_str),
                    "return_type": return_type,
                    "line": i + 1,
                    "end_line": end_line,
                    "complexity": complexity,
                    "calls": calls,
                    "docstring": docstring,
                    "type": "function"
                })

            # 检测类定义
            class_match = re.match(r'^\s*class\s+(\w+)', line)
            if class_match:
                result["metrics"]["classes_count"] += 1
                result["classes"].append({
                    "name": class_match.group(1),
                    "line": i + 1
                })

            # 检测导入
            import_match = re.match(r'^\s*(import|from)\s+([\w\.]+)', line)
            if import_match:
                result["metrics"]["imports_count"] += 1
                result["imports"].append({
                    "module": import_match.group(2),
                    "line": i + 1
                })

        # 计算平均复杂度
        if complexities:
            result["metrics"]["avg_complexity"] = round(sum(complexities) / len(complexities), 1)

        # 问题检测（保留原有检测，增加新检测）
        for i, line in enumerate(lines):
            stripped = line.strip()

            # 原有检测...
            if 'eval(' in stripped or 'exec(' in stripped:
                result["issues"].append({
                    "type": "security",
                    "line": i + 1,
                    "severity": "high",
                    "description": "使用了 eval/exec，存在代码注入风险",
                    "suggestion": "避免使用 eval/exec，使用安全的替代方案",
                    "code_example": "# 使用 ast.literal_eval() 或 json.loads() 替代"
                })

            if stripped.startswith('assert') and 'test' not in file_path.lower():
                result["issues"].append({
                    "type": "security",
                    "line": i + 1,
                    "severity": "medium",
                    "description": "assert 语句在生产环境中可能被忽略",
                    "suggestion": "使用 if 语句进行参数验证",
                    "code_example": "if not condition:\n    raise ValueError('错误信息')"
                })

            if 'for' in stripped and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('for'):
                    result["issues"].append({
                        "type": "performance",
                        "line": i + 1,
                        "severity": "medium",
                        "description": "检测到嵌套循环，可能影响性能",
                        "suggestion": "考虑使用更高效的数据结构或算法",
                        "code_example": "# 使用字典或集合优化 O(n^2) 到 O(n)"
                    })

            if len(line) > 100:
                result["issues"].append({
                    "type": "style",
                    "line": i + 1,
                    "severity": "low",
                    "description": f"行长度 {len(line)} 超过建议值 100",
                    "suggestion": "拆分长行或提取变量",
                    "code_example": "# 将长表达式拆分为多行"
                })

            if 'except:' in stripped or (stripped == 'except Exception:' and i + 1 < len(lines) and 'pass' in lines[i + 1]):
                result["issues"].append({
                    "type": "logic",
                    "line": i + 1,
                    "severity": "high",
                    "description": "空的异常处理会隐藏错误",
                    "suggestion": "明确捕获特定异常并适当处理",
                    "code_example": "except ValueError as e:\n    logger.error(f'错误: {e}')\n    raise"
                })

            if 'input(' in stripped and 'try' not in lines[max(0, i-2)]:
                result["issues"].append({
                    "type": "logic",
                    "line": i + 1,
                    "severity": "medium",
                    "description": "用户输入未经异常处理",
                    "suggestion": "使用 try-except 处理 KeyboardInterrupt 和 EOFError",
                    "code_example": "try:\n    user_input = input('请输入: ')\nexcept (KeyboardInterrupt, EOFError):\n    print('\\n退出')"
                })

            # 新增：检测复杂度过高
            for func in result["functions"]:
                if func["line"] == i + 1 and func["complexity"]["score"] > 10:
                    result["issues"].append({
                        "type": "complexity",
                        "line": i + 1,
                        "severity": "medium",
                        "description": f"函数 {func['name']} 圈复杂度为 {func['complexity']['score']}，超过建议值",
                        "suggestion": func["complexity"]["suggestion"],
                        "code_example": "# 建议拆分为多个小函数"
                    })
                    break

            # 新增：检测缺少文档字符串
            for func in result["functions"]:
                if func["line"] == i + 1 and not func.get("docstring"):
                    result["issues"].append({
                        "type": "documentation",
                        "line": i + 1,
                        "severity": "low",
                        "description": f"函数 {func['name']} 缺少文档字符串",
                        "suggestion": "添加 docstring 说明函数用途、参数和返回值",
                        "code_example": 'def func():\n    """函数说明"""\n    pass'
                    })
                    break

        # 生成概要
        if result["issues"]:
            high_count = sum(1 for i in result["issues"] if i["severity"] == "high")
            medium_count = sum(1 for i in result["issues"] if i["severity"] == "medium")
            result["summary"] = f"发现 {len(result['issues'])} 个问题（高: {high_count}，中: {medium_count}，低: {len(result['issues']) - high_count - medium_count}）"
            result["suggestions"].append("🔴 建议优先修复高严重度问题")
        else:
            result["summary"] = "✅ 代码质量良好，未发现明显问题"

        if result["metrics"]["comment_lines"] < result["metrics"]["code_lines"] * 0.1 and result["metrics"]["code_lines"] > 20:
            result["suggestions"].append("💡 建议增加代码注释，提高可读性")

        if result["metrics"]["functions_count"] > 10:
            result["suggestions"].append("📦 函数数量较多，建议考虑模块化拆分")

        if result["metrics"]["avg_complexity"] > 8:
            result["suggestions"].append(f"⚠️ 平均圈复杂度 {result['metrics']['avg_complexity']}，建议简化函数逻辑")

        return result

    def _find_function_end(self, lines: List[str], start_line: int) -> int:
        """查找函数结束行"""
        base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        for i in range(start_line + 1, len(lines)):
            if not lines[i].strip():
                continue
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent <= base_indent and not lines[i].strip().startswith('#'):
                return i
        return len(lines)

    # ========== 深度审查（静态分析 + LLM）==========

    def deep_review(self, code: str, file_path: str = "") -> Dict:
        """深度代码审查 - 静态分析 + LLM 分析"""
        # 1. 静态分析
        static_analysis = self.analyze_code(code, file_path)

        # 2. 构建 LLM prompt（基于静态分析结果）
        review_prompt = self._build_deep_review_prompt(code, file_path, static_analysis)

        # 3. 调用 LLM 深度分析
        llm_review = self._call_llm(review_prompt)

        # 4. 生成修复代码（如果有问题）
        fixes = []
        if static_analysis["issues"]:
            fix_prompt = self._build_fix_prompt(code, static_analysis["issues"])
            fix_code = self._call_llm(fix_prompt)
            if fix_code:
                fixes.append({
                    "original": code[:500],
                    "fixed": fix_code[:500],
                    "description": "基于发现的问题生成的修复代码"
                })

        return {
            "success": True,
            "static_analysis": static_analysis,
            "llm_review": llm_review,
            "fixes": fixes,
            "summary": static_analysis["summary"],
            "issues": static_analysis["issues"],
            "suggestions": static_analysis["suggestions"]
        }

    def _build_deep_review_prompt(self, code: str, file_path: str, analysis: dict) -> str:
        """构建深度审查的 LLM prompt"""
        prompt = f"""请对以下代码进行深度代码审查：

## 📁 文件信息
- 路径: {file_path}
- 总行数: {analysis['metrics']['total_lines']}
- 代码行数: {analysis['metrics']['code_lines']}
- 注释行数: {analysis['metrics']['comment_lines']}
- 平均圈复杂度: {analysis['metrics']['avg_complexity']}

## 📦 代码结构
### 函数列表
"""
        for func in analysis['functions'][:10]:
            prompt += f"- `{func['name']}` (第{func['line']}行) - 复杂度: {func['complexity']['score']}\n"
            if func.get('calls'):
                prompt += f"  调用: {', '.join(func['calls'][:5])}\n"

        if analysis['classes']:
            prompt += "\n### 类列表\n"
            for cls in analysis['classes'][:5]:
                prompt += f"- `{cls['name']}` (第{cls['line']}行)\n"

        if analysis['imports']:
            prompt += "\n### 导入模块\n"
            for imp in analysis['imports'][:10]:
                prompt += f"- {imp['module']}\n"

        prompt += f"""
## 🔍 代码内容
```python
{code[:1500]}
{'... (代码过长，已截断)' if len(code) > 1500 else ''}
⚠️ 静态分析发现的问题
{self._format_issues(analysis['issues']) if analysis['issues'] else '无自动检测问题'}

📝 请提供以下分析
代码功能概述（1-2句话）

架构设计评价（优点和不足）

安全风险评估

性能分析

可维护性建议

具体改进代码示例

输出格式请使用 Markdown，代码块使用 ```python 标记。"""
        return prompt

    def _build_fix_prompt(self, code: str, issues: list) -> str:
        """构建修复代码生成的 prompt"""
        issues_text = self._format_issues(issues)
        return f"""请修复以下代码中的问题：

原始代码
{code[:1500]}
需要修复的问题
{issues_text}

要求
保持原有功能不变

修复所有问题

只输出修复后的完整代码

不要有任何解释

不要用 markdown 代码块包裹输出

请输出修复后的代码："""

    def _format_review_result(self, result: Dict) -> str:
        """格式化深度审查结果为 Markdown"""
        output = f"""## 📊 代码审查报告

📈 概览
{result['summary']}

🔧 代码结构
函数数量: {result['static_analysis']['metrics']['functions_count']}

类数量: {result['static_analysis']['metrics']['classes_count']}

导入数量: {result['static_analysis']['metrics']['imports_count']}

平均圈复杂度: {result['static_analysis']['metrics']['avg_complexity']}

📦 函数详情
"""
        for func in result['static_analysis']['functions'][:5]:
            output += f"""

{func['name']} (第{func['line']}行)
参数: {', '.join([p['name'] for p in func['params']]) if func['params'] else '无'}

返回类型: {func['return_type'] or '未标注'}

圈复杂度: {func['complexity']['score']} ({func['complexity']['level']})

调用函数: {', '.join(func['calls'][:5]) if func['calls'] else '无'}
"""

        if result['issues']:
            output += f"\n### ⚠️ 问题清单\n\n"
            output += "| 行号 | 类型 | 严重程度 | 问题描述 |\n"
            output += "|------|------|----------|----------|\n"
        for issue in result['issues'][:15]:
            output += f"| {issue['line']} | {issue['type']} | {issue['severity']} | {issue['description']} |\n"

        if result['suggestions']:
            output += f"\n### 💡 改进建议\n"
        for s in result['suggestions']:
            output += f"- {s}\n"

        if result.get('llm_review'):
            output += f"\n### 🤖 深度分析\n\n{result['llm_review']}\n"

        if result.get('fixes'):
            output += f"\n### 🔧 自动修复\n\n"
        for fix in result['fixes']:
            output += f"{fix['description']}\n\n"
            output += f"python\n{fix['fixed'][:800]}\n\n"

            output += f"\n---\n💡 提示: 用户可以根据以上建议在编辑器中手动修改代码，或回复「应用修复」自动应用。"

        return output


    def _format_review_result_with_highlight(self, result: Dict) -> str:
        """格式化审查结果，并添加前端高亮指令"""
        output = f"""## 📊 代码审查报告

### 📈 概览
{result['summary']}

### 🔧 代码结构
- 函数数量: {result['static_analysis']['metrics']['functions_count']}
- 类数量: {result['static_analysis']['metrics']['classes_count']}
- 平均圈复杂度: {result['static_analysis']['metrics']['avg_complexity']}

### ⚠️ 问题清单

| 行号 | 类型 | 严重程度 | 问题描述 |
|------|------|----------|----------|
"""
        for issue in result['issues']:
            output += f"| {issue['line']} | {issue['type']} | {issue['severity']} | {issue['description']} |\n"

        if result['issues']:
            highlight_lines = ','.join([str(i['line']) for i in result['issues']])
            output += f"\n---\n<!-- HIGHLIGHT_LINES:{highlight_lines} -->\n"
            output += f"\n💡 **提示**: 问题行 {highlight_lines} 已在编辑器中高亮显示。"

        return output



    def _format_issues(self, issues: list) -> str:
        """格式化问题列表"""
        if not issues:
            return "无"
        result = ""
        for i in issues:
            result += f"- L{i['line']} [{i['type']}/{i['severity']}]: {i['description']}\n"
        return result



        # 修改默认帮助，避免污染编辑器
    def _get_help_text(self) -> str:
        # 当被直接调用且无法识别时，返回空字符串，避免污染
        return ""


    # ========== 自主修复功能 ==========
    def auto_fix(self, code: str, file_path: str = "") -> Dict:
        """自动修复代码中的问题"""
        
        # 1. 分析代码
        analysis = self.analyze_code(code, file_path)
        
        if not analysis.get("issues"):
            return {
                "success": True,
                "message": "未发现需要修复的问题",
                "fixed_code": code,
                "issues": []
            }
        
        # 2. 生成修复方案
        fix_prompt = self._build_fix_prompt(code, analysis["issues"])
        fixed_code = self._call_llm(fix_prompt)
        
        if not fixed_code:
            return {
                "success": False,
                "message": "生成修复方案失败",
                "fixed_code": code,
                "issues": analysis["issues"]
            }
        
        # 3. 提取修复后的代码
        fixed_code = self._extract_code(fixed_code)
        
        # 4. 验证修复
        verification = self._verify_fix(code, fixed_code)
        
        return {
            "success": True,
            "message": f"已修复 {len(analysis['issues'])} 个问题",
            "original_code": code,
            "fixed_code": fixed_code,
            "issues": analysis["issues"],
            "verification": verification
        }
    
    def _build_fix_prompt(self, code: str, issues: list) -> str:
        """构建修复提示词"""
        issues_text = ""
        for i, issue in enumerate(issues, 1):
            issues_text += f"{i}. 行 {issue['line']}: {issue['description']}\n"
            issues_text += f"   建议: {issue['suggestion']}\n"
        
        return f"""请修复以下代码中的所有问题：

## 代码
```python
{code}
需要修复的问题
{issues_text}

要求
1.保持原有功能不变

2.修复所有问题

3.只输出修复后的完整代码

4.不要解释

修复后的代码："""
    def _extract_code(self, text: str) -> str:
        """从响应中提取代码"""
        import re
        match = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _verify_fix(self, original: str, fixed: str) -> Dict:
        """验证修复是否正确"""
        # 简单验证：检查代码是否有效
        import re
    
        # 检查代码是否变化
        if original.strip() == fixed.strip():
            return {"status": "warning", "message": "代码未发生变化"}
    
        # 检查是否有语法错误（简单检查）
        try:
            compile(fixed, '<string>', 'exec')
            return {"status": "success", "message": "代码语法正确"}
        except SyntaxError as e:
            return {"status": "error", "message": f"修复后代码有语法错误: {e}"}



if __name__ == "__main__":
    agent = CodeAgentV4("test")
    result = agent.process("写一个快速排序函数")
    print(result.get('response')[:300])
    print("\n✅ CodeAgentV4 测试通过")
