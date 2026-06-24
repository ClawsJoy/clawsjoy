""" -  do_anything """

import re

from core.lib.llm_client import llm_client


class TranslateSkill:
    name = "translate"
    description = "文本翻译"
    version = "2.8.0"
    category = "text"

    def execute(self, goal=None, params=None, **kwargs):
        """兼容 do_anything 调用"""

        # 处理各种参数格式
        text = None

        # 情况1: goal 是字符串
        if isinstance(goal, str):
            text = goal
        # 情况2: goal 是 dict (do_anything 可能传 dict)
        elif isinstance(goal, dict):
            text = goal.get("goal", "") or goal.get("text", "")
        # 情况3: params 中有 goal
        elif params and isinstance(params, dict):
            text = params.get("goal", "")
        # 情况4: kwargs 中
        elif kwargs:
            text = kwargs.get("goal", "") or kwargs.get("text", "")

        if not text:
            return {
                "success": False,
                "error": "请提供要翻译的文本",
                "response": "翻译失败",
            }

        # 确保 text 是字符串
        if isinstance(text, dict):
            text = str(text)

        original_text = text.strip()

        # 提取要翻译的内容
        if original_text.startswith("翻译"):
            content = original_text[2:].strip()
        else:
            content = original_text

        if not content:
            return {
                "success": False,
                "error": "请提供要翻译的文本",
                "response": "翻译失败",
            }

        # 本地映射
        local_map = {
            "hello": "你好",
            "world": "世界",
            "good morning": "早上好",
            "good night": "晚安",
            "thank you": "谢谢",
            "thanks": "谢谢",
            "hi": "你好",
            "how are you": "你好吗",
            "i love you": "我爱你",
        }

        lower_content = content.lower()
        if lower_content in local_map:
            return {
                "success": True,
                "result": local_map[lower_content],
                "response": local_map[lower_content],
                "source": "local",
            }

        # 使用 Ollama 翻译
        try:
            prompt = f"请将以下文本翻译成中文，只输出翻译结果：\n{content}"
            response = llm_client.generate(prompt=prompt, model="qwen2.5:3b", max_tokens=512, temperature=0.7, task_type="skill")
            if response.status_code == 200:
                result = response.json().get("response", "")
                result = re.sub(r"^（我是 ClawsJoy 助手）", "", result)
                result = result.strip()
                if result:
                    return {
                        "success": True,
                        "result": result,
                        "response": result,
                        "source": "ollama",
                    }
        except Exception as e:
            print(f"Ollama 翻译失败: {e}")

        return {
            "success": True,
            "result": content,
            "response": content,
            "source": "fallback",
        }


skill = TranslateSkill()
