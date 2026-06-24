import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 _handle_start_novel 方法中添加保存逻辑
old_start = '''    def _handle_start_novel(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
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

现在开始写："""
        result = self._call_llm(prompt)
        return result'''

new_start = '''    def _handle_start_novel(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """① 直接创作小说正文 + 自动保存"""
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

现在开始写："""
        result = self._call_llm(prompt)
        
        # ========== 自动保存 ==========
        import os
        from datetime import datetime
        
        # 创建保存目录
        save_dir = "projects/novels"
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '_', topic[:20])
        filename = f"{save_dir}/{safe_topic}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"💾 小说已保存: {filename}")
        
        return result + f"\n\n---\n💾 已自动保存到: {filename}"'''

content = content.replace(old_start, new_start)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ writer_agent 已添加自动保存功能")
print("   - 保存目录: projects/novels/")
print("   - 文件名: {主题}_{时间戳}.txt")
