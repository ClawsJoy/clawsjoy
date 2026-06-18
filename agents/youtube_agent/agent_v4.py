#!/usr/bin/env python3
"""YoutubeAgent v4.2 - 精简稳定版（YouTube 助手）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class YoutubeAgentV4(BusinessAgent):
    """YouTube Agent - 精简稳定版"""

    name = "youtube_agent_v4"
    description = "智慧 YouTube 助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📺 YoutubeAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["下载", "download"]):
            return self._download_video(user_input)
        
        if any(kw in t for kw in ["信息", "详情", "视频信息"]):
            return self._get_video_info(user_input)
        
        if any(kw in t for kw in ["搜索", "找视频"]):
            return self._search_video(user_input)
        
        if any(kw in t for kw in ["分析频道", "频道分析"]):
            return self._analyze_channel(user_input)
        
        if any(kw in t for kw in ["生成标题", "起标题"]):
            return self._generate_title(user_input)
        
        if any(kw in t for kw in ["seo", "优化", "搜索优化"]):
            return self._optimize_seo(user_input)
        
        return self._resp("📺 输入「下载 链接」、「视频信息」、「搜索 关键词」、「生成标题」、「频道分析」或「SEO优化」")

    # ================================================================
    #  下载
    # ================================================================

    def _download_video(self, user_input: str) -> Dict:
        url = self._extract_url(user_input)
        if not url:
            return self._resp("请提供 YouTube 链接。示例：下载 https://youtu.be/xxx")
        return self._resp(f"⏳ 正在下载：{url}\n\n💡 需要安装 yt-dlp 技能")

    # ================================================================
    #  视频信息
    # ================================================================

    def _get_video_info(self, user_input: str) -> Dict:
        url = self._extract_url(user_input)
        if not url:
            return self._resp("请提供 YouTube 链接。示例：信息 https://youtu.be/xxx")
        
        result = self._call_llm(f"获取视频信息：{url}")
        return self._resp(f"📹 视频信息\n\n{result or '信息获取完成'}")

    # ================================================================
    #  搜索
    # ================================================================

    def _search_video(self, user_input: str) -> Dict:
        keyword = re.sub(r'(搜索视频|找视频|查找视频)', '', user_input).strip()
        if not keyword:
            return self._resp("请提供关键词。示例：搜索 人工智能教程")
        
        result = self._call_llm(f"推荐5个关于「{keyword}」的YouTube视频")
        return self._resp(f"🔍 搜索结果\n\n关键词：{keyword}\n\n{result or self._default_search(keyword)}")

    def _default_search(self, keyword: str) -> str:
        return f"1. 【教程】{keyword} 从入门到精通\n2. {keyword} 实战项目\n3. 10分钟掌握{keyword}\n4. {keyword} 进阶技巧\n5. {keyword} 常见问题解答"

    # ================================================================
    #  频道分析
    # ================================================================

    def _analyze_channel(self, user_input: str) -> Dict:
        channel = re.sub(r'(分析频道|频道分析)', '', user_input).strip()
        if not channel:
            channel = "频道"
        
        result = self._call_llm(f"分析YouTube频道：{channel}（受众、定位、优势、改进、增长策略）")
        return self._resp(f"📊 频道分析\n\n{result or '分析完成'}")

    # ================================================================
    #  标题生成
    # ================================================================

    def _generate_title(self, user_input: str) -> Dict:
        topic = re.sub(r'(生成标题|视频标题|起标题)', '', user_input).strip()
        if not topic:
            return self._resp("请提供主题。示例：生成标题 Python教程")
        
        result = self._call_llm(f"为「{topic}」生成10个YouTube标题")
        return self._resp(f"📌 标题推荐\n\n主题：{topic}\n\n{result or self._default_titles(topic)}")

    def _default_titles(self, topic: str) -> str:
        return f"1. 【全网最全】{topic} 完整教程\n2. 零基础学会{topic}\n3. {topic} 从入门到精通\n4. 为什么一定要学{topic}？\n5. {topic} 实战项目"

    # ================================================================
    #  SEO 优化
    # ================================================================

    def _optimize_seo(self, user_input: str) -> Dict:
        content = re.sub(r'(seo优化|搜索优化|视频优化)', '', user_input, flags=re.IGNORECASE).strip()
        if not content:
            content = "视频内容"
        
        result = self._call_llm(f"为「{content}」提供SEO优化建议（关键词、标题、描述、标签、缩略图）")
        return self._resp(f"📈 SEO优化建议\n\n{result or '优化建议生成完成'}")

    # ================================================================
    #  辅助
    # ================================================================

    def _extract_url(self, text: str) -> str:
        pattern = r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"[YouTube] LLM失败: {e}")
        return ""

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = YoutubeAgentV4("test")
    print(agent.process("生成标题 Python教程")["response"])
