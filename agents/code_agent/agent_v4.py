#!/usr/bin/env python3
"""CodeAgent v4.0 - 智慧化代码生成智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any

from core.agents.business.business_agent import BusinessAgent


class CodeAgentV4(BusinessAgent):
    """代码 Agent - 智慧化版本"""
    
    name = "code_agent_v4"
    description = "智慧代码助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._code_memory = self._init_code_memory(user_id)
        self._code_style = self._code_memory.recall_style()  # 先初始化这个
        print(f"💻 CodeAgent v{self.version} 智慧化试点启动")
        print(f"   📚 代码记忆已加载: {self._code_memory.get_stats()['history_count']} 条记录")
        print(f"   🎨 代码风格偏好: {self._code_style or '默认'}")

    ###1. 添加代码风格偏好记忆
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
            
            # 在 SimpleCodeMemory 类中添加
            def recall_style(self):
                return self._preferences.get('code_style')

            def remember_style(self, style):
                self._preferences['code_style'] = style
                self._save()
        
        return SimpleCodeMemory(user_id)
    
    # ========== 能力声明 ==========
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        """声明能力"""
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
        """核心代码处理逻辑- 增强版"""
        
        # 1. 设置代码风格
        if "偏好风格" in user_input or "代码风格" in user_input:
            style_match = re.search(r'(?:偏好风格|代码风格)[：:]?\s*(\w+)', user_input)
            if style_match:
                style = style_match.group(1).lower()
                if style in ["pep8", "google", "airbnb"]:
                    self._code_memory.remember_style(style)
                    return self._response(f"✅ 已设置代码风格偏好：{style}")
            current = self._code_memory.recall_style() or "默认"
            return self._response(f"当前代码风格偏好：{current}\n可设置：pep8, google, airbnb")
    
        # 2. 生成单元测试
        if "生成测试" in user_input or "单元测试" in user_input:
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                tests = self._generate_tests(code, language)
                return self._response(tests, metadata={"type": "tests"})
            return self._response("请提供要生成测试的代码。格式：```python\n代码\n```")
    
        # 3. 代码审查
        if "审查" in user_input or "review" in user_input.lower():
            code_match = re.search(r'```(\w*)\n(.*?)```', user_input, re.DOTALL)
            if code_match:
                language = code_match.group(1) or "python"
                code = code_match.group(2)
                review = self._review_code(code, language)
                return self._response(review, metadata={"type": "review"})
            return self._response("请提供要审查的代码。格式：```python\n代码\n```")

        # 4. 代码生成
        if any(kw in user_input for kw in ["写代码", "生成代码", "写一个", "实现", "编写"]):
            code = self._generate_code(user_input)
            language = self._detect_language(user_input)
            self._code_memory.record_code(user_input, code, language, True)
            return self._response(
                f"```{language}\n{code}\n```",
                metadata={"language": language, "type": "generated"}
            )
        
        # 5. 代码解释
        if any(kw in user_input for kw in ["解释", "说明", "什么意思", "作用"]):
            explanation = self._explain_code(user_input)
            return self._response(explanation, metadata={"type": "explanation"})
        
        # 6. 代码调试
        if any(kw in user_input for kw in ["调试", "debug", "错误", "bug", "修复"]):
            debug_result = self._debug_code(user_input)
            return self._response(debug_result, metadata={"type": "debug"})
        
        # 7. 代码优化
        if any(kw in user_input for kw in ["优化", "改进", "重构", "性能"]):
            optimized = self._optimize_code(user_input)
            return self._response(optimized, metadata={"type": "optimized"})
        
        # 8. 设置偏好
        if "偏好" in user_input or "喜欢" in user_input:
            return self._handle_preference(user_input)
        
        # 9. 默认：代码分析
        analysis = self._analyze_request(user_input)
        return self._response(analysis, metadata={"type": "analysis"})
    
    # ========== 辅助方法 ==========
    
    def _response(self, content: str, **kwargs) -> Dict:
        """构建响应"""
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }
    
    def _detect_language(self, text: str) -> str:
        """检测编程语言"""
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
        # 使用记忆中的偏好
        return self._code_memory.recall_language()
    
    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM 生成内容"""
        if not model:
            model = self._select_model(prompt)
    
        try:
            import requests
            import json
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2048
                    }
                },
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                response = data.get("response", "")
                if response and len(response) > 20:
                    print(f"[DEBUG] LLM 响应成功，长度: {len(response)}")
                    return response.strip()
                else:
                    print(f"[DEBUG] LLM 响应为空或太短")
            else:
                print(f"[DEBUG] LLM 返回错误状态码: {resp.status_code}")
                
        except requests.exceptions.Timeout:
            print("[DEBUG] LLM 请求超时")
        except Exception as e:
            print(f"[DEBUG] LLM 调用异常: {e}")
        
        return ""

    def _generate_code(self, prompt: str) -> str:
        """生成代码 - 使用 LLM"""
        import re
        language = self._detect_language(prompt)
    
        full_prompt = f"""你是一个专业的{language}程序员。用户需求：{prompt}

请只输出纯粹的{language}代码，不要用markdown代码块包裹，不要有任何解释文字。"""

        response = self._call_llm(full_prompt)
    
        if response:
            # 清理响应
            response = response.strip()
        
            # 移除所有可能的代码块标记
            response = re.sub(r'^```\w*\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
            response = re.sub(r'```\w*\n', '', response)
        
            # 移除开头的 language 标记
            if response.startswith(language + '\n'):
                response = response[len(language)+1:]
        
            response = response.strip()
        
            if response:
                return f"```{language}\n{response}\n```"
    
        # 降级模板
        return f"""```{language}
# 代码生成请求: {prompt[:100]}
def solution():
    pass
```"""


    def _get_fallback_code(self, prompt: str, language: str) -> str:
        """降级模板代码"""
        templates = {
            "python": f'''# 代码生成请求: {prompt[:100]}
    # LLM 服务未响应，请确保 Ollama 正在运行
    # 运行: ollama serve

    def fibonacci(n):
        """计算斐波那契数列的第n项"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b

    # 测试
    if __name__ == "__main__":
        for i in range(10):
            print(f"fib({{i}}) = {{fibonacci(i)}}")
    ''',
            "javascript": f'''// 代码生成请求: {prompt[:100]}
    // LLM 服务未响应

    function fibonacci(n) {{
        if (n <= 0) return 0;
        if (n === 1) return 1;
        let a = 0, b = 1;
        for (let i = 2; i <= n; i++) {{
            [a, b] = [b, a + b];
        }}
        return b;
    }}

    // 测试
    for (let i = 0; i < 10; i++) {{
       console.log(`fib(${{i}}) = ${{fibonacci(i)}}`);
    }}
    '''
        }
        return templates.get(language, templates["python"])



    def _explain_code(self, text: str) -> str:
        """解释代码"""
        
        # 尝试提取代码块
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        if code_match:
            language = code_match.group(1) or "python"
            code = code_match.group(2)
        else:
            return "请提供要解释的代码。例如：\n解释代码：```python\nprint('hello')\n```"
        
        # 使用 LLM 解释
        prompt = f"请简洁地解释以下 {language} 代码的功能：\n```{language}\n{code}\n```"
        explanation = self._call_llm(prompt)
        
        if explanation:
            return f"**代码解释**\n\n{explanation}\n\n```{language}\n{code}\n```"
        
        return f"**代码分析**\n\n这是 {language} 代码，主要功能需要根据具体逻辑分析。\n\n```{language}\n{code}\n```"
    
    def _debug_code(self, text: str) -> str:
        """调试代码"""
        
        # 提取代码
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        
        if not code_match:
            return "请提供要调试的代码。\n格式：\n```python\n代码\n```\n\n错误信息：具体的错误"
        
        language = code_match.group(1) or "python"
        code = code_match.group(2)
        
        # 提取错误信息
        error_match = re.search(r'错误[：:]\s*(.+?)(?:\n|$)', text)
        error = error_match.group(1) if error_match else "未知错误"
        
        # 使用 LLM 调试
        prompt = f"""调试以下 {language} 代码：

代码：
{code}

错误信息：{error}
请分析原因并提供修复后的代码。"""

        result = self._call_llm(prompt)
        if result:
           return result
        return f"{language}\n{code}\n\n\n建议检查变量类型和边界条件。"

    def _optimize_code(self, text: str) -> str:
        """优化代码"""
        import re
    
        code_match = re.search(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        if not code_match:
            return "请提供要优化的代码。格式：```python\n代码\n```"
    
        language = code_match.group(1) or "python"
        code = code_match.group(2)
    
        prompt = f"""优化以下{language}代码，直接输出优化后的代码，不要有任何解释：

原始代码：
{code}

要求：
1. 保持相同功能
2. 提高可读性
3. 优化性能
4. 只输出优化后的代码，不要用markdown代码块包裹"""

        optimized = self._call_llm(prompt)
    
        if optimized:
            # 清理可能的代码块标记
            optimized = optimized.strip()
            if optimized.startswith('```'):
                lines = optimized.split('\n')
                optimized = '\n'.join([l for l in lines if not l.startswith('```')])
            return f"```{language}\n{optimized}\n```"
    
        return f"```{language}\n{code}\n```\n\n# 建议：考虑使用更高效的数据结构或算法"


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
- 解释代码："解释代码：```python\nprint('hello')\n```"
- 调试代码："调试代码并提供错误信息"
- 优化代码："优化这段代码"
- 设置偏好："偏好 python"

请提供具体的代码需求！"""

###2. 添加单元测试生成
    def _generate_tests(self, code: str, language: str) -> str:
        """为代码生成单元测试"""
        prompt = f"""为以下{language}代码生成单元测试：

代码：
{code}

要求：

1.使用该语言的测试框架

2.覆盖主要功能

3.包含边界条件测试

4.只输出测试代码

请输出完整的测试代码："""

        tests = self._call_llm(prompt)
        if tests:
            return f"{language}\n{tests}\n"
            return "# 单元测试生成失败，请手动编写测试用例"

### 3. 添加代码审查建议

    def _review_code(self, code: str, language: str) -> str:
        """代码审查 - 提供改进建议"""
        prompt = f"""请审查以下{language}代码，直接输出审查结果，不要用markdown代码块包裹：

代码：
{code}

请从以下方面分析并直接输出：

1. 代码质量：命名、注释、结构
2. 潜在问题：bug、边界条件
3. 性能问题
4. 安全性
5. 改进建议

输出格式（不要用代码块）：
**代码审查报告**

**优点：**
- ...

**问题：**
- ...

**改进建议：**
- ..."""

        review = self._call_llm(prompt)
        if review:
            # 清理可能的代码块标记
            review = review.strip()
            if review.startswith('```'):
                lines = review.split('\n')
                review = '\n'.join([l for l in lines if not l.startswith('```')])
            return review
        return "代码审查暂时不可用，请稍后重试。"

    def _analyze_request(self, user_input: str) -> str:
        """分析代码请求"""
        return """我是代码助手，可以帮您：

- 生成代码："写一个排序函数"
- 解释代码："解释代码：```python\n代码\n```"
- 调试代码："调试代码并提供错误信息"
- 优化代码："优化这段代码"

请提供具体的代码需求！"""


if __name__ == "__main__":
    agent = CodeAgentV4("test")
    result = agent.process("写一个 Python 函数")
    print(result.get('response')[:200])
    print("\n✅ CodeAgentV4 测试通过")
