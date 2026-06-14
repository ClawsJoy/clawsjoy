#!/usr/bin/env python3
"""CodeAgent v4.0 - 智慧化代码生成智能体（优化版）"""

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
    """代码 Agent - 智慧化版本（优化版）"""

    name = "code_agent_v4"
    description = "智慧代码助手"
    version = "4.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._code_memory = self._init_code_memory(user_id)
        self._code_style = self._code_memory.recall_style()
        self._code_repo = get_code_repo(user_id)  # 添加代码库
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
        }
        return capabilities.get((action, target), (False, 0.0))

    # ========== 核心业务逻辑 ==========

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心代码处理逻辑 - 优先处理代码生成"""
        
        # ========== 0. 代码库操作 ==========
        # 添加项目
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

        # 列出项目
        if "列出项目" in user_input or "我的项目" in user_input:
            projects = self._code_repo.list_projects()
            if not projects:
                return self._response("还没有添加项目。使用「添加项目 /项目路径」")
            lines = ["📁 **我的项目**"]
            for p in projects:
                lines.append(f"  • {p['name']} ({p['languages']}) - {p['file_count']} 个文件")
            return self._response("\n".join(lines))

        # 搜索代码
        if "搜索代码" in user_input or "查找代码" in user_input:
            match = re.search(r'(?:搜索代码|查找代码)[：:]?\s*(.+)', user_input)
            if match:
                query = match.group(1).strip()
                results = self._code_repo.search_code(query)
                if results:
                    lines = [f"🔍 搜索 '{query}' 找到 {len(results)} 个文件:"]
                    for r in results[:10]:
                        lines.append(f"  • {r['file']} ({r.get('language', 'unknown')})")
                    return self._response("\n".join(lines))
                return self._response(f"未找到包含 '{query}' 的文件")
            return self._response("请提供搜索关键词。示例：搜索代码 main")

        # 读取项目文件
        if "读取文件" in user_input:
            match = re.search(r'读取文件[：:]?\s*(\S+)', user_input)
            if match:
                file_path = match.group(1)
                projects = self._code_repo.list_projects()
                if projects:
                    # 在第一个项目中查找
                    content = self._code_repo.get_file_content(projects[0]["id"], file_path)
                    if content:
                        preview = content[:500] + "..." if len(content) > 500 else content
                        return self._response(f"📄 **{file_path}**\n\n```\n{preview}\n```")
                return self._response(f"未找到文件: {file_path}")
            return self._response("请提供文件名。示例：读取文件 main.py")
        # ========== 0. 通用代码生成（最高优先级）==========
        # 匹配各种代码请求格式
        is_code_request = False
        code_task = user_input
        
        # 匹配 "写xxx" 格式
        if re.match(r'^写[一个|一段|个]?\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^写[一个|一段|个]?\s*', '', user_input)
        
        # 匹配 "生成xxx" 格式
        elif re.match(r'^生成\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^生成\s*', '', user_input)
        
        # 匹配 "实现xxx" 格式
        elif re.match(r'^实现\s', user_input):
            is_code_request = True
            code_task = re.sub(r'^实现\s*', '', user_input)
        
        # 匹配包含关键词
        elif any(kw in user_input for kw in ["代码", "函数", "算法", "程序"]):
            # 排除非代码请求
            if not any(kw in user_input for kw in ["解释", "说明", "调试", "优化", "审查"]):
                is_code_request = True
        
        if is_code_request:
            code = self._generate_code(code_task)
            language = self._detect_language(user_input)
            self._code_memory.record_code(user_input, code, language, True)
            return self._response(
                f"```{language}\n{code}\n```",
                metadata={"language": language, "type": "generated"}
            )

        # ========== 1. 设置代码风格 ==========
        if "偏好风格" in user_input or "代码风格" in user_input:
            style_match = re.search(r'(?:偏好风格|代码风格)[：:]?\s*(\w+)', user_input)
            if style_match:
                style = style_match.group(1).lower()
                if style in ["pep8", "google", "airbnb"]:
                    self._code_memory.remember_style(style)
                    return self._response(f"✅ 已设置代码风格偏好：{style}")
            current = self._code_memory.recall_style() or "默认"
            return self._response(f"当前代码风格偏好：{current}\n可设置：pep8, google, airbnb")

        # ========== 2. 生成单元测试 ==========
        if "生成测试" in user_input or "单元测试" in user_input:
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                tests = self._generate_tests(code, language)
                return self._response(tests, metadata={"type": "tests"})
            return self._response("请提供要生成测试的代码。格式：```python\n代码\n```")

        # ========== 3. 代码审查 ==========
        if "审查" in user_input or "review" in user_input.lower():
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                review = self._review_code(code, language)
                return self._response(review, metadata={"type": "review"})
            return self._response("请提供要审查的代码。格式：```python\n代码\n```")

        # ========== 4. 代码解释 ==========
        if any(kw in user_input for kw in ["解释", "说明", "什么意思", "作用"]):
            explanation = self._explain_code(user_input)
            return self._response(explanation, metadata={"type": "explanation"})

        # ========== 5. 代码调试 ==========
        if any(kw in user_input for kw in ["调试", "debug", "错误", "bug", "修复"]):
            debug_result = self._debug_code(user_input)
            return self._response(debug_result, metadata={"type": "debug"})

        # ========== 6. 代码优化 ==========
        if any(kw in user_input for kw in ["优化", "改进", "重构", "性能"]):
            optimized = self._optimize_code(user_input)
            return self._response(optimized, metadata={"type": "optimized"})

        # ========== 7. 设置偏好 ==========
        if "偏好" in user_input or "喜欢" in user_input:
            return self._handle_preference(user_input)

        # ========== 8. 默认帮助 ==========
        return self._response(self._get_help_text())

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

    def _generate_code(self, prompt: str) -> str:
        """生成代码 - 使用 LLM"""
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
            # 移除可能存在的代码块标记
            response = re.sub(r'^```\w*\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
            return response
        
        # 降级模板
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
- 设置偏好："偏好 python"

请提供具体的代码需求！"""

    def _analyze_request(self, user_input: str) -> str:
        return self._get_help_text()


if __name__ == "__main__":
    agent = CodeAgentV4("test")
    result = agent.process("写一个快速排序函数")
    print(result.get('response')[:300])
    print("\n✅ CodeAgentV4 测试通过")

       
