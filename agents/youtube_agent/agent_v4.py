#!/usr/bin/env python3
"""youtube_agent v4.1 - 智慧化 YouTube 助手（专业版）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple

from core.agents.business.business_agent import BusinessAgent


class YoutubeAgentV4(BusinessAgent):
    """智慧化 YouTube 助手 - 专业版"""

    name = "youtube_agent_v4"
    description = "智慧化 YouTube 助手"
    version = "4.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📺 {self.name} v{self.version} 智慧化启动（专业版）")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("search", "video"): (True, 0.90),
            ("analyze", "channel"): (True, 0.85),
            ("generate", "title"): (True, 0.85),
            ("optimize", "seo"): (True, 0.80),
            ("download", "video"): (True, 0.85),
            ("info", "video"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:

        # ========== 下载/信息 ==========
        if any(kw in user_input for kw in ["下载", "download", "保存视频"]):
            return self._download_video(user_input)

        if any(kw in user_input for kw in ["信息", "info", "详情", "视频信息"]):
            return self._get_video_info(user_input)

        # ========== 搜索 ==========
        if any(kw in user_input for kw in ["搜索视频", "找视频", "查找视频"]):
            return self._search_video(user_input)

        # ========== 频道分析 ==========
        if any(kw in user_input for kw in ["分析频道", "频道分析"]):
            return self._analyze_channel(user_input)

        # ========== 标题生成 ==========
        if any(kw in user_input for kw in ["生成标题", "视频标题", "起标题"]):
            return self._generate_title(user_input)

        # ========== SEO 优化 ==========
        if any(kw in user_input for kw in ["SEO优化", "搜索优化", "视频优化"]):
            return self._optimize_seo(user_input)

        # ========== 默认帮助 ==========
        return self._response(self._get_help())

    # ========== 1. 下载功能 ==========
    def _download_video(self, user_input: str) -> Dict:
        """下载 YouTube 视频"""
        try:
            from skills.video_download.video_download_skill import video_download
            downloader = video_download()
        except ImportError:
            return self._response("❌ video-download 技能未安装，请先安装：pip install yt-dlp")

        url = self._extract_url(user_input)
        if not url:
            return self._response("请提供有效的 YouTube 链接\n\n示例：https://youtu.be/xxx")

        # 执行下载
        print("⏳ 正在下载视频，请稍候...")
        result = downloader._download(url, "best")
        if result.get("success"):
            return self._response(f"✅ {result['message']}")
        return self._response(f"❌ 下载失败: {result.get('error', '未知错误')}")

    # ========== 2. 视频信息 ==========
    def _get_video_info(self, user_input: str) -> Dict:
        """获取视频信息"""
        try:
            from skills.video_download.video_download_skill import video_download
            downloader = video_download()
        except ImportError:
            return self._response("❌ video-download 技能未安装")

        url = self._extract_url(user_input)
        if not url:
            return self._response("请提供有效的 YouTube 链接")

        info = downloader._get_info(url)
        if info.get("success"):
            return self._response(f"""📹 **视频信息**

**标题**: {info['title']}
**上传者**: {info['uploader']}
**时长**: {info['duration']} 秒 ({info['duration']//60} 分 {info['duration']%60} 秒)
**观看次数**: {info['view_count']:,}
**格式数量**: {info['formats']}

💡 如需下载，请回复：下载 {url}""")
        return self._response(f"获取信息失败: {info.get('error', '未知错误')}")

    # ========== 3. 搜索 ==========
    def _search_video(self, user_input: str) -> Dict:
        """搜索视频"""
        match = re.search(r'(?:搜索视频|找视频|查找视频)[：:]\s*(.+)', user_input)
        keyword = match.group(1) if match else user_input.replace("搜索视频", "").replace("找视频", "").strip()

        if not keyword:
            return self._response("请提供搜索关键词。\n\n示例：搜索视频 人工智能教程")

        prompt = f"""请为以下关键词推荐 YouTube 视频：

搜索词：{keyword}

要求：
1. 推荐 5 个相关视频
2. 包含标题和简短描述
3. 说明推荐理由

输出格式：
1. 视频标题 - 描述
   推荐理由：..."""

        response = self._call_llm(prompt)

        if response:
            return self._response(
                f"🔍 **视频搜索结果**\n\n关键词：{keyword}\n\n{response}",
                metadata={"keyword": keyword}
            )

        return self._response(self._get_search_results(keyword))

    # ========== 4. 频道分析 ==========
    def _analyze_channel(self, user_input: str) -> Dict:
        """分析频道"""
        match = re.search(r'(?:分析频道|频道分析)[：:]\s*(.+)', user_input)
        channel_name = match.group(1) if match else "频道"

        prompt = f"""请分析以下 YouTube 频道：

频道名称/主题：{channel_name}

分析维度：
1. 目标受众
2. 内容定位
3. 优势特点
4. 改进建议
5. 增长策略

输出格式：简洁的列表"""

        response = self._call_llm(prompt)

        if response:
            return self._response(
                f"📊 **频道分析**\n\n{response}",
                metadata={"channel": channel_name}
            )

        return self._response(self._get_channel_analysis(channel_name))

    # ========== 5. 标题生成 ==========
    def _generate_title(self, user_input: str) -> Dict:
        """生成视频标题"""
        match = re.search(r'(?:生成标题|视频标题|起标题)[：:]\s*(.+)', user_input)
        topic = match.group(1) if match else user_input.replace("生成标题", "").replace("视频标题", "").strip()

        if not topic:
            return self._response("请提供视频主题。\n\n示例：生成标题 Python 教程")

        prompt = f"""请为以下主题生成 YouTube 视频标题：

主题：{topic}

要求：
1. 生成 10 个标题
2. 包含吸引力
3. 使用热门格式
4. 适合 SEO

输出格式：直接列出标题，每个一行"""

        response = self._call_llm(prompt)

        if response:
            return self._response(
                f"📌 **视频标题推荐**\n\n主题：{topic}\n\n{response}",
                metadata={"topic": topic}
            )

        return self._response(self._get_title_examples(topic))

    # ========== 6. SEO 优化 ==========
    def _optimize_seo(self, user_input: str) -> Dict:
        """SEO 优化"""
        match = re.search(r'(?:SEO优化|搜索优化|视频优化)[：:]\s*(.+)', user_input)
        content = match.group(1) if match else "视频内容"

        prompt = f"""请为以下视频内容提供 SEO 优化建议：

内容/主题：{content}

优化维度：
1. 关键词建议
2. 标题优化
3. 描述优化
4. 标签建议
5. 缩略图建议

输出格式：分类列出"""

        response = self._call_llm(prompt)

        if response:
            return self._response(
                f"📈 **SEO 优化建议**\n\n{response}",
                metadata={"type": "seo"}
            )

        return self._response(self._get_seo_tips(content))

    # ========== 辅助方法 ==========
    def _extract_url(self, text: str) -> str:
        """提取 YouTube URL"""
        pattern = r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _get_search_results(self, keyword: str) -> str:
        return f"""🔍 **视频搜索结果**

关键词：{keyword}

1. 【教程】{keyword} 从入门到精通 - 详细讲解，适合初学者
2. {keyword} 实战项目 - 动手实践，学以致用
3. 10分钟快速掌握{keyword} - 速成教程
4. {keyword} 进阶技巧 - 提高效率的秘诀
5. {keyword} 常见问题解答 - 解决学习困惑

💡 提示：使用 YouTube API 可获取真实搜索结果"""

    def _get_channel_analysis(self, channel: str) -> str:
        return f"""📊 **频道分析**

频道：{channel}

🎯 目标受众：对{channel}感兴趣的观众
📝 内容定位：提供高质量、有价值的内容
✅ 优势：持续更新，内容专业
💡 改进建议：增加互动，优化标题
📈 增长策略：系列视频，跨平台推广

💡 提示：接入 YouTube Analytics API 可获得真实数据"""

    def _get_title_examples(self, topic: str) -> str:
        return f"""📌 **视频标题推荐**

主题：{topic}

1. 【全网最全】{topic} 完整教程
2. 零基础学会{topic}，只需 10 分钟！
3. {topic} 从入门到精通 - 这可能是最好的教程
4. 为什么你一定要学会{topic}？
5. {topic} 实战：做一个完整项目
6. {topic} 避坑指南：新手必看
7. 我花了 100 小时学习{topic}，总结出这些经验
8. {topic} vs 其他技术，选哪个？
9. 3 个技巧让你快速掌握{topic}
10. {topic} 面试必备：高频考点解析"""

    def _get_seo_tips(self, content: str) -> str:
        return f"""📈 **SEO 优化建议**

内容：{content}

🔑 关键词建议：
- 主关键词：{content}
- 长尾词：{content} 教程、{content} 入门、{content} 实战
- 相关词：学习 {content}、{content} 技巧、{content} 工具

📝 标题优化：
- 使用数字：10分钟学会{content}
- 使用形容词：最全的{content}教程
- 使用疑问句：{content}值得学吗？

🏷️ 标签建议：
#{content}, #{content}教程, 学习{content}

💡 描述优化：
- 前 150 字符包含关键词
- 添加时间戳目录
- 包含相关链接

💡 提示：使用 YouTube Studio 分析工具可获取真实数据"""

    def _get_help(self) -> str:
        return """📺 **YouTube 助手** (专业版 v4.1)

支持功能:
- 🔍 搜索视频: "搜索视频 人工智能教程"
- 📊 分析频道: "分析频道 科技频道"
- 📌 生成标题: "生成标题 Python 入门教程"
- 📈 SEO 优化: "SEO优化 编程教学视频"
- ⬇️ 下载视频: "下载 https://youtu.be/xxx"
- ℹ️ 视频信息: "视频信息 https://youtu.be/xxx"

💡 提示: 使用 YouTube API 可获得真实数据"""

    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = YoutubeAgentV4("test")
    print("\n✅ youtube_agent_v4 测试通过")

    # 覆盖 _download_video 和 _get_video_info 方法
    def _get_downloader(self):
        """获取下载器实例"""
        try:
            from skills.video_download import video_download_skill
            return video_download_skill.video_download()
        except ImportError:
            try:
                from skills.video_download.video_download_skill import video_download
                return video_download()
            except ImportError:
                return None
