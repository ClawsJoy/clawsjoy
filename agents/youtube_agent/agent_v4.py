#!/usr/bin/env python3
"""YoutubeAgent v4.3 - API Key 方案（YouTube Data API v3）"""

import sys
import os
import re
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
load_dotenv("config/.env")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.agents.business.business_agent import BusinessAgent


class YoutubeAgentV4(BusinessAgent):
    """YouTube Agent - API Key 方案"""

    name = "youtube_agent_v4"
    description = "智慧 YouTube 助手"
    version = "5.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.youtube = None
        if self.api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
                print(f"📺 YoutubeAgent v{self.version} 启动 ✅ (API Key)")
            except Exception as e:
                print(f"📺 YoutubeAgent v{self.version} 启动 ⚠️ (API 初始化失败: {e})")
        else:
            print(f"📺 YoutubeAgent v{self.version} 启动 ⚠️ (未配置 YOUTUBE_API_KEY)")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        # 1. 下载
        if any(kw in t for kw in ["下载", "download"]):
            return self._download_video(user_input)

        # 2. 视频信息
        if any(kw in t for kw in ["信息", "详情", "视频信息"]):
            return self._get_video_info(user_input)

        # 3. SEO 优化 ← 提到搜索前面
        if any(kw in t for kw in ["seo", "搜索优化"]):
            return self._optimize_seo(user_input)

        # 4. 搜索
        if any(kw in t for kw in ["搜索", "找视频", "搜"]):
            return self._search_video(user_input)

        # 5. 频道分析
        if any(kw in t for kw in ["分析频道", "频道分析"]):
            return self._analyze_channel(user_input)

        # 6. 标题生成
        if any(kw in t for kw in ["生成标题", "起标题"]):
            return self._generate_title(user_input)

        # 7. 兜底
        if any(kw in t for kw in ["youtube", "油管", "yt"]):
            return self._search_video(user_input)

        return self._resp("📺 ...")


    # ================================================================
    #  下载（已跑通，不改）
    # ================================================================
    def _download_video(self, user_input: str) -> Dict:
        url = self._extract_url(user_input)
        if not url:
            return self._resp("请提供 YouTube 链接。示例：下载 https://youtu.be/xxx")

        try:
            from skills.video_download.video_download_skill import video_download
            result = video_download().execute({"url": url})
            if result.get("success"):
                return self._resp(f"✅ 下载完成\n\n{result.get('file', result.get('message', ''))}")
            else:
                return self._resp(f"❌ 下载失败：{result.get('error', '未知错误')}")
        except Exception as e:
            return self._resp(f"❌ 下载失败：{e}")

    # ================================================================
    #  视频信息（API Key 方案）
    # ================================================================
    def _get_video_info(self, user_input: str) -> Dict:
        url = self._extract_url(user_input)
        if not url:
            return self._resp("请提供 YouTube 链接。示例：信息 https://youtu.be/xxx")

        video_id = self._extract_video_id(url)
        if not video_id:
            return self._resp("无法提取视频 ID，请检查链接格式")

        if not self.youtube:
            return self._resp("YouTube API 未配置，请在 config/.env 中设置 YOUTUBE_API_KEY")

        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()

            if not response.get("items"):
                return self._resp(f"未找到视频: {video_id}")

            item = response["items"][0]
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            details = item.get("contentDetails", {})

            # 解析时长
            duration = self._parse_duration(details.get("duration", ""))

            info = (
                f"📹 **{snippet.get('title', '未知')}**\n\n"
                f"**频道**: {snippet.get('channelTitle', '未知')}\n"
                f"**发布时间**: {snippet.get('publishedAt', '未知')[:10]}\n"
                f"**时长**: {duration}\n"
                f"**播放量**: {self._format_number(stats.get('viewCount', '0'))}\n"
                f"**点赞**: {self._format_number(stats.get('likeCount', '0'))}\n"
                f"**评论**: {self._format_number(stats.get('commentCount', '0'))}\n\n"
                f"**描述**: {snippet.get('description', '无')[:300]}"
            )
            return self._resp(info)
        except Exception as e:
            return self._resp(f"获取视频信息失败: {e}")

    # ================================================================
    #  搜索（API Key 方案）
    # ================================================================
    def _search_video(self, user_input: str) -> Dict:
        keyword = re.sub(r'(搜索视频|找视频|查找视频|搜索|搜|油管|youtube|帮我|找几个|找)', '', user_input, flags=re.IGNORECASE).strip()
        if not keyword:
            return self._resp("请提供关键词。示例：搜索 人工智能教程")

        if not self.youtube:
            return self._resp("YouTube API 未配置，请在 config/.env 中设置 YOUTUBE_API_KEY")

        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=5
            )
            response = request.execute()

            if not response.get("items"):
                return self._resp(f"未找到关于「{keyword}」的视频")

            lines = [f"🔍 **搜索结果**: {keyword}\n"]
            for i, item in enumerate(response["items"], 1):
                snippet = item["snippet"]
                video_id = item["id"]["videoId"]
                title = snippet.get("title", "未知")
                channel = snippet.get("channelTitle", "未知")
                lines.append(
                    f"{i}. **{title}**\n"
                    f"   频道: {channel}\n"
                    f"   链接: https://youtu.be/{video_id}\n"
                )

            return self._resp("\n".join(lines))
        except Exception as e:
            return self._resp(f"搜索失败: {e}")

    # ================================================================
    #  频道分析（API Key 方案）
    # ================================================================
    def _analyze_channel(self, user_input: str) -> Dict:
        channel = re.sub(r'(分析频道|频道分析)', '', user_input).strip()
        if not channel:
            return self._resp("请提供频道名称或 ID。示例：分析频道 Google")

        if not self.youtube:
            return self._resp("YouTube API 未配置，请在 config/.env 中设置 YOUTUBE_API_KEY")

        try:
            # 先搜索频道
            search_request = self.youtube.search().list(
                part="snippet",
                q=channel,
                type="channel",
                maxResults=1
            )
            search_response = search_request.execute()

            if not search_response.get("items"):
                return self._resp(f"未找到频道: {channel}")

            channel_id = search_response["items"][0]["snippet"]["channelId"]

            # 获取频道详情
            channel_request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            channel_response = channel_request.execute()

            if not channel_response.get("items"):
                return self._resp(f"无法获取频道信息: {channel}")

            item = channel_response["items"][0]
            snippet = item["snippet"]
            stats = item.get("statistics", {})

            info = (
                f"📊 **频道分析**: {snippet.get('title', '未知')}\n\n"
                f"**订阅者**: {self._format_number(stats.get('subscriberCount', '0'))}\n"
                f"**总播放量**: {self._format_number(stats.get('viewCount', '0'))}\n"
                f"**视频数**: {self._format_number(stats.get('videoCount', '0'))}\n"
                f"**创建时间**: {snippet.get('publishedAt', '未知')[:10]}\n"
                f"**国家/地区**: {snippet.get('country', '未知')}\n\n"
                f"**描述**: {snippet.get('description', '无')[:300]}"
            )
            return self._resp(info)
        except Exception as e:
            return self._resp(f"频道分析失败: {e}")

    # ================================================================
    #  标题生成（LLM，不改）
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
    #  SEO 优化（LLM，不改）
    # ================================================================
    def _optimize_seo(self, user_input: str) -> Dict:
        content = re.sub(r'(seo优化|搜索优化|视频优化)', '', user_input, flags=re.IGNORECASE).strip()
        if not content:
            content = "视频内容"

        result = self._call_llm(f"为「{content}」提供SEO优化建议（关键词、标题、描述、标签、缩略图）")
        return self._resp(f"📈 SEO优化建议\n\n{result or '优化建议生成完成'}")

    # ================================================================
    #  辅助方法
    # ================================================================
    def _extract_url(self, text: str) -> str:
        pattern = r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/))[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _extract_video_id(self, url: str) -> str:
        """从 YouTube URL 提取视频 ID"""
        # youtu.be/xxx
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        # youtube.com/watch?v=xxx
        match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        # youtube.com/shorts/xxx
        match = re.search(r'shorts/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        return ""

    def _parse_duration(self, duration: str) -> str:
        """解析 ISO 8601 时长为可读格式"""
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return duration
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        parts = []
        if h:
            parts.append(f"{h}小时")
        if m:
            parts.append(f"{m}分钟")
        if s:
            parts.append(f"{s}秒")
        return "".join(parts) if parts else "0秒"

    def _format_number(self, num_str: str) -> str:
        """格式化数字（如 12345 → 1.2万）"""
        try:
            num = int(num_str)
        except (ValueError, TypeError):
            return num_str
        if num >= 100000000:
            return f"{num/100000000:.1f}亿"
        elif num >= 10000:
            return f"{num/10000:.1f}万"
        else:
            return f"{num:,}"

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = YoutubeAgentV4("test")
    print(agent.process("信息 https://youtu.be/dQw4w9WgXcQ")["response"])
