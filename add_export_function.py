import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 1. 添加 _export_to_txt 方法（在文件末尾，_resp 之前）
export_method = '''
    def _export_to_txt(self) -> str:
        """导出小说为 txt 文件"""
        import os
        from datetime import datetime

        # 生成文件名
        title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '_', self._novel.get('title', '未命名')[:20])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.txt"

        # 确保目录存在
        export_dir = "exports/novels"
        os.makedirs(export_dir, exist_ok=True)

        filepath = os.path.join(export_dir, filename)

        # 构建完整内容
        lines = []
        lines.append(f"《{self._novel.get('title', '未命名')}》")
        lines.append(f"体裁：{self._novel.get('genre', '未指定')}")
        lines.append(f"主题：{self._novel.get('theme', '')}")
        lines.append(f"创作日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        # 大纲
        lines.append("【大纲】")
        lines.append(self._novel.get('outline', '无大纲'))
        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        # 角色
        if self._novel.get('characters'):
            lines.append("【角色】")
            for char in self._novel['characters']:
                lines.append(char.get('profile', ''))
                lines.append("")
            lines.append("=" * 60)
            lines.append("")

        # 各章节
        lines.append("【正文】")
        lines.append("")
        for chapter in self._novel.get('chapters', []):
            lines.append(f"## {chapter.get('title', f'第{chapter.get(\"number\", 0)}章')}")
            lines.append("")
            lines.append(chapter.get('content', ''))
            lines.append("")
            lines.append("-" * 40)
            lines.append("")

        # 统计
        lines.append("=" * 60)
        lines.append(f"总字数：{self._count_words()} 字")
        lines.append(f"章节数：{len(self._novel.get('chapters', []))} 章")
        lines.append(f"角色数：{len(self._novel.get('characters', []))} 个")

        content = "\n".join(lines)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

'''

# 在 _resp 方法之前插入
content = content.replace(
    '    def _resp(self, content: str, **kwargs) -> Dict:',
    export_method + '\n    def _resp(self, content: str, **kwargs) -> Dict:'
)

# 2. 修改 _handle_complete 添加导出
old_complete = '''        self._novel["status"] = "completed"
        self._save_state()

        return f\"\"\"
🎉 小说完成！'''

new_complete = '''        self._novel["status"] = "completed"
        self._save_state()

        # 导出为 txt
        try:
            filepath = self._export_to_txt()
            export_msg = f\"\\n\\n📁 已导出为：{filepath}\"
        except Exception as e:
            export_msg = f\"\\n\\n⚠️ 导出失败：{e}\"

        return f\"\"\"
🎉 小说完成！'''

content = content.replace(old_complete, new_complete)

# 在导出消息后添加统计
# 找到 return 中的统计部分，在 export_msg 后面加入
content = re.sub(
    r'(字数：约 \{words\} 字)(\n\n📊 \*\*统计\*\*)',
    r'\1\nexport_msg\2',
    content
)

# 但更稳妥的方式是用字符串替换
content = content.replace(
    '字数：约 {words} 字\n\n📊 **统计**',
    '字数：约 {words} 字{export_msg}\n\n📊 **统计**'
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ writer_agent 已添加导出功能")
