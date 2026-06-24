import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 _handle_start_novel：直接生成小说正文，而不是大纲
old_start_novel = '''    def _handle_start_novel(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """① 灵感孵化 → 完整大纲"""
        # 提取主题
        topic = re.sub(r'^(写小说|创作小说|开始写小说|新小说)', '', user_input).strip()
        if not topic:
            topic = "一个动人的故事"

        # 检测体裁
        genre = "通用"
        for g in ["科幻", "奇幻", "悬疑", "爱情", "动作", "喜剧", "悲剧", "史诗"]:
            if g in user_input:
                genre = g
                break

        prompt = f"""请为一篇小说创作完整大纲：
【主题】{topic}
【体裁】{genre}

请输出：
1. 故事梗概（100-200字）
2. 主要角色（至少2个，含姓名、性格、动机）
3. 故事结构（开端-发展-高潮-结局）
4. 关键情节节点（3-5个）
5. 主题与核心冲突
6. 结尾方向

输出格式：直接列出，不要用表格。"""'''
new_start_novel = '''    def _handle_start_novel(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """① 直接创作小说正文"""
        # 提取主题
        topic = re.sub(r'^(写小说|创作小说|开始写小说|新小说)', '', user_input).strip()
        if not topic:
            topic = "一个动人的故事"

        # 检测体裁
        genre = "通用"
        for g in ["科幻", "奇幻", "悬疑", "爱情", "动作", "喜剧", "悲剧", "史诗"]:
            if g in user_input:
                genre = g
                break

        # 检测风格
        style = "温暖现实"
        for s in ["村上春树", "海明威", "张爱玲", "鲁迅", "金庸"]:
            if s in user_input:
                style = s
                break

        prompt = f"""请写一部完整的短篇小说（2000-3000字）。

【主题】{topic}
【体裁】{genre}
【风格】{style}

写作要求：
1. 直接写小说正文，不要有任何大纲标记
2. 有完整的场景描写（画面、声音、气味）
3. 有真实的人物对话（带引号）
4. 有内心独白
5. 有开头、发展、高潮、结尾
6. 段落流畅连贯
7. 像真正的小说一样

现在开始写："""'''
content = content.replace(old_start_novel, new_start_novel)

# 修复路由：确保 start_novel 调用直接写小说的 prompt
# 在 _execute_processor 中找到 start_novel 的映射
content = content.replace(
    '"start_novel": self._handle_outline,',
    '"start_novel": self._handle_start_novel,'
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ writer_agent 已修复")
print("   - _handle_start_novel 现在直接写小说正文")
print("   - 路由映射已更新")
