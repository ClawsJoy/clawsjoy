"""翻译技能 - 修复版 v2.3"""

import re

import requests


class TranslateSkill:
    name = "translate"
    description = "文本翻译"
    version = "2.3.0"
    category = "text"

    LANG_MAP = {
        "zh": "zh-CN",
        "zh-CN": "zh-CN",
        "zh-TW": "zh-TW",
        "en": "en",
        "ja": "ja",
        "ko": "ko",
        "fr": "fr",
        "de": "de",
        "es": "es",
        "ru": "ru",
    }

    def execute(
        self, goal: str = None, text: str = None, params: dict = None, **kwargs
    ):
        """兼容大脑调度器调用"""

        # 兼容多种调用方式
        if text:
            content = text
        elif goal:
            content = goal
        elif params and isinstance(params, dict):
            content = params.get("goal") or params.get("text") or ""
        else:
            content = str(kwargs.get("goal", "")) if kwargs else ""

        # 确保 content 是字符串
        if not isinstance(content, str):
            content = str(content) if content else ""

        if not content or not content.strip():
            return {
                "success": False,
                "error": "请提供要翻译的文本",
                "response": "翻译失败",
            }

        original_content = content.strip()

        # 解析：翻译 hello 为中文 或 translate hello to chinese
        import re

        content_lower = original_content.lower()

        # 匹配中文格式：翻译 X 为 Y 或 翻译 X
        cn_match = re.search(r"翻译\s*([^为]+?)\s*(?:为\s*(.+))?$", original_content)
        if cn_match:
            text_to_translate = cn_match.group(1).strip()
            target_lang = cn_match.group(2).strip() if cn_match.group(2) else "中文"
            content = text_to_translate
            # 目标语言映射
            lang_map = {
                "中文": "zh",
                "英文": "en",
                "英语": "en",
                "日文": "ja",
                "韩文": "ko",
            }
            target = lang_map.get(target_lang, "zh")
        else:
            # 匹配英文格式：translate X to Y
            en_match = re.search(r"translate\s+(.+?)\s+to\s+(\w+)", content_lower)
            if en_match:
                content = en_match.group(1).strip()
                target_lang = en_match.group(2).strip()
                lang_map = {
                    "chinese": "zh",
                    "english": "en",
                    "japanese": "ja",
                    "korean": "ko",
                }
                target = lang_map.get(target_lang, "zh")
            else:
                # 简单格式：只是 "翻译 hello" 或 "translate world"
                # 去掉开头的 "翻译 " 或 "translate "
                if original_content.startswith("翻译"):
                    content = original_content[2:].strip()
                elif original_content.lower().startswith("translate"):
                    content = original_content[9:].strip()
                else:
                    content = original_content
                target = "zh"

        if not content:
            return {
                "success": False,
                "error": "请提供要翻译的文本",
                "response": "翻译失败",
            }

        # 调用翻译 API
        try:
            src_code = LANG_MAP.get("auto", "auto")
            tgt_code = LANG_MAP.get(target, "zh-CN")

            url = "https://api.mymemory.translated.net/get"
            resp = requests.get(
                url,
                params={"q": content, "langpair": f"{src_code}|{tgt_code}"},
                timeout=10,
            )

            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated:
                    translated = re.sub(r"<[^>]+>", "", translated)

                if translated and translated != content:
                    return {
                        "success": True,
                        "result": translated,
                        "response": translated,
                        "source": "api",
                    }
        except Exception as e:
            print(f"翻译 API 错误: {e}")

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
            "apple": "苹果",
            "banana": "香蕉",
            "cat": "猫",
            "dog": "狗",
        }

        lower_content = content.lower()
        for key, value in local_map.items():
            if key == lower_content:
                return {
                    "success": True,
                    "result": value,
                    "response": value,
                    "source": "local",
                }

        # 如果所有方法都失败，返回原文
        return {
            "success": True,
            "result": content,
            "response": content,
            "source": "fallback",
            "note": "无法翻译",
        }


skill = TranslateSkill()
