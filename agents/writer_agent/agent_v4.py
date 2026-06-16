#!/usr/bin/env python3
"""writer_agent v4.0 - 智慧化文案写作智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent


class WriterAgentV4(BusinessAgent):
    """智慧化文案写作智能体"""
    
    name = "writer_agent_v4"
    description = "智慧化文案助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._writing_history = []
        print(f"✍️ {self.name} v{self.version} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("write", "text"): (True, 0.95),
            ("polish", "text"): (True, 0.90),
            ("summarize", "text"): (True, 0.90),
            ("rewrite", "text"): (True, 0.85),
            ("change_style", "text"): (True, 0.85),
            ("continue", "text"): (True, 0.85),
            ("translate", "text"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 写作/撰写
        if any(kw in user_input for kw in ["写", "撰写", "创作", "编写"]):
            return self._write(user_input)
        
        # 润色/优化
        if any(kw in user_input for kw in ["润色", "优化", "改进", "美化"]):
            return self._polish(user_input)
        
        # 总结/摘要
        if any(kw in user_input for kw in ["总结", "摘要", "概括", "归纳"]):
            return self._summarize(user_input)
        
        # 重写/改写

        # 风格转换
        if any(kw in user_input for kw in ["转换风格", "风格转换", "改写为"]):
            return self.change_style(user_input)

        # 续写
        if any(kw in user_input for kw in ["续写", "继续写"]):
            return self.continue_writing(user_input)
        if any(kw in user_input for kw in ["重写", "改写", "换种说法"]):
            return self._rewrite(user_input)
        
        return self._response(self._get_help())
    
    def _write(self, user_input: str) -> Dict:
        """撰写文案"""
        # 提取写作主题和类型
        topic = user_input
        
        # 检测写作类型
        writing_type = "general"
        if "邮件" in user_input or "email" in user_input.lower():
            writing_type = "email"
        elif "报告" in user_input:
            writing_type = "report"
        elif "文章" in user_input:
            writing_type = "article"
        elif "朋友圈" in user_input or "微博" in user_input:
            writing_type = "social"
        elif "广告" in user_input or "营销" in user_input:
            writing_type = "ad"
        elif "诗歌" in user_input:
            writing_type = "poem"
        
        # 提取具体内容
        content = re.sub(r'^写.*?[：:]', '', user_input)
        if not content or content == user_input:
            content = re.sub(r'^(写|撰写|创作|编写)', '', user_input)
        
        if not content.strip():
            return self._response("请告诉我你想写什么内容。\n\n示例：\n- 写一封邮件给客户介绍产品\n- 写一篇关于人工智能的文章")
        
        # 根据类型构建 prompt
        prompts = {
            "email": f"请写一封专业的邮件，主题是：{content}\n要求：格式规范、语气得体、内容清晰。",
            "report": f"请写一份简洁的报告，内容关于：{content}\n要求：结构清晰、重点突出、数据准确。",
            "article": f"请写一篇短文，主题是：{content}\n要求：语言流畅、观点明确、引人入胜。",
            "social": f"请写一条社交媒体文案，内容是：{content}\n要求：简洁有趣、有吸引力、适合分享。",
            "ad": f"请写一段广告文案，内容是：{content}\n要求：有说服力、突出卖点、引人注目。",
            "poem": f"请写一首关于{content}的诗\n要求：有意境、押韵、优美。",
            "general": f"请写一段文字，内容是：{content}\n要求：通顺流畅、表达清晰。"
        }
        
        prompt = prompts.get(writing_type, prompts["general"])
        response = self._call_llm(prompt)
        
        if response:
            # 记录写作历史
            self._writing_history.append({
                "type": writing_type,
                "topic": content[:50],
                "result": response[:200],
                "timestamp": datetime.now().isoformat()
            })
            return self._response(
                f"✍️ **{self._get_type_name(writing_type)}**\n\n{response}",
                metadata={"type": writing_type}
            )
        
        return self._response(self._get_sample(content, writing_type))
    
    def _polish(self, user_input: str) -> Dict:
        """润色文案"""
        # 提取要润色的内容
        content = re.sub(r'^润色|优化|改进|美化[：:]?', '', user_input)
        
        if not content.strip():
            return self._response("请提供要润色的内容。\n\n示例：润色 这段文字需要改进...")
        
        prompt = f"""请润色以下文字，使其更优美、流畅：

原文：{content}

要求：
1. 保持原意
2. 改进表达
3. 优化语言
4. 只输出润色后的结果"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"✨ **润色结果**\n\n**原文：**\n{content}\n\n**润色后：**\n{response}",
                metadata={"original": content, "polished": response}
            )
        
        return self._response(f"润色后的文字：\n\n{content}\n\n(请确保 LLM 服务正在运行)")
    
    def _summarize(self, user_input: str) -> Dict:
        """总结摘要"""
        content = re.sub(r'^总结|摘要|概括|归纳[：:]?', '', user_input)
        
        if not content.strip():
            return self._response("请提供要总结的内容。\n\n示例：总结 这是一段很长的文字...")
        
        prompt = f"""请为以下内容生成简洁的摘要：

{content}

要求：
1. 提取核心观点
2. 保留关键信息
3. 语言简洁
4. 只输出摘要"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📝 **内容摘要**\n\n**原文：**\n{content[:200]}...\n\n**摘要：**\n{response}",
                metadata={"summary": response}
            )
        
        return self._response(f"内容摘要：\n\n{content[:200]}...\n\n(请确保 LLM 服务正在运行)")
    
    def _rewrite(self, user_input: str) -> Dict:
        """重写文案"""
        content = re.sub(r'^重写|改写|换种说法[：:]?', '', user_input)
        
        if not content.strip():
            return self._response("请提供要重写的内容。\n\n示例：重写 这段文字需要换个风格")
        
        prompt = f"""请用不同的表达方式重写以下内容：

原文：{content}

要求：
1. 保持原意
2. 换一种风格
3. 语言更生动
4. 只输出重写后的结果"""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🔄 **重写结果**\n\n**原文：**\n{content}\n\n**重写后：**\n{response}",
                metadata={"rewritten": response}
            )
        
        return self._response(f"重写结果：\n\n{content}\n\n(请确保 LLM 服务正在运行)")
    
    def _get_type_name(self, writing_type: str) -> str:
        """获取写作类型名称"""
        names = {
            "email": "邮件",
            "report": "报告",
            "article": "文章",
            "social": "社交媒体",
            "ad": "广告文案",
            "poem": "诗歌",
            "general": "文字"
        }
        return names.get(writing_type, "文字")
    
    def _get_sample(self, topic: str, writing_type: str) -> str:
        """获取示例文案（降级方案）"""
        samples = {
            "email": f"**邮件示例**\n\n主题：{topic}\n\n尊敬的客户：\n\n您好！感谢您的关注。\n\n[具体内容]\n\n此致\n敬礼",
            "social": f"**朋友圈文案**\n\n{topic}\n\n✨ 今日分享 ✨\n\n#美好生活 #分享快乐",
            "article": f"**文章开头**\n\n{topic}\n\n在这个信息爆炸的时代，{topic}成为了我们关注的焦点...",
            "general": f"**写作内容**\n\n{topic}\n\n{topic}是一个值得深入探讨的话题..."
        }
        return samples.get(writing_type, samples["general"])
    
    def _get_help(self) -> str:
        return """✍️ **文案助手**

支持功能:
- 📝 写作: "写一封邮件给客户" / "写一篇关于AI的文章"
- ✨ 润色: "润色 这段话需要改进"
- 📋 总结: "总结 这段长文字"
- 🔄 重写: "重写 这段内容换个风格"

写作类型:
- 邮件 (email)
- 报告 (report)
- 文章 (article)
- 社交媒体 (social)
- 广告文案 (ad)
- 诗歌 (poem)

💡 提示: 提供越详细的要求，效果越好"""
    
    def _response(self: 'WriterAgentV4', content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }

    # ========== 增强：风格转换和续写 ==========

    def change_style(self, user_input: str) -> Dict:
        """转换写作风格"""
        # 解析风格和目标文本
        # 格式：转换风格 幽默 这段文字内容
        parts = user_input.split()
        if len(parts) < 2:
            return self._response("请指定风格。示例：转换风格 幽默 今天天气很好")
        
        style = parts[1] if len(parts) > 1 else "幽默"
        content = ' '.join(parts[2:]) if len(parts) > 2 else user_input
        
        styles = {
            "幽默": "幽默风趣、轻松诙谐，带点调侃",
            "正式": "正式专业、严谨规范，用词考究",
            "文艺": "文艺诗意、优美抒情，富有感染力",
            "简洁": "简洁明了、直击重点，去除冗余",
            "热情": "热情积极、充满活力，有感染力",
            "商务": "商务正式、专业得体，礼貌周到"
        }
        
        style_desc = styles.get(style, f"{style}风格")
        
        prompt = f"""请将以下内容改写为{style_desc}风格：

原文：{content}

要求：
1. 保持原意不变
2. 语气符合{style}风格
3. 只输出改写后的结果

改写后："""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"🎨 **{style}风格改写**\n\n**原文：**\n{content}\n\n**改写后：**\n{response}",
                metadata={"style": style, "original": content, "rewritten": response}
            )
        
        return self._response(f"风格转换失败，请确保 LLM 服务正常运行")
    
    def continue_writing(self, user_input: str) -> Dict:
        """续写文章"""
        # 提取续写的前文
        content = re.sub(r'^续写[：:]?', '', user_input).strip()
        
        if not content:
            return self._response("请提供要续写的文本。示例：续写 很久很久以前，有一个...")
        
        prompt = f"""请根据以下前文继续写作：

前文：{content}

要求：
1. 保持风格一致
2. 自然衔接前文
3. 续写 100-200 字
4. 只输出续写内容

续写："""
        
        response = self._call_llm(prompt)
        
        if response:
            return self._response(
                f"📝 **续写结果**\n\n**前文：**\n{content}\n\n**续写：**\n{response}",
                metadata={"previous": content, "continued": response}
            )
        
        return self._response(f"续写失败，请确保 LLM 服务正常运行")


if __name__ == "__main__":
    from datetime import datetime
    agent = WriterAgentV4("test")
    print("✅ writer_agent_v4 测试通过")
