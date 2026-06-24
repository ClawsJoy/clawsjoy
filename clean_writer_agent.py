import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 删除的方法列表
methods_to_remove = [
    '_handle_export_to',
    '_handle_export',
    '_build_export_operations',
    '_extract_path',
    '_get_project_title',
    '_export_to_txt',
]

for method in methods_to_remove:
    # 匹配从 def method_name 到下一个 def 或类结束
    pattern = rf'\n    def {method}\(.*?\)(?::.*?)(?=\n    def |\nclass |\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# 删除 _execute_business 中的导出检测
content = re.sub(
    r'        # ========== 0. 导出意图检测（优先） ==========\n        if any\(kw in user_input for kw in \["导出到", "导出项目到", "保存到"\]\):\n            return self\._handle_export_to\(user_input, context\)\n        if any\(kw in user_input for kw in \["导出", "导出项目", "导出完整版", "导出章节", "导出大纲", "导出角色"\]\):\n            return self\._handle_export\(user_input, context\)\n',
    '',
    content
)

# 删除 _handle_complete 中的导出逻辑
content = re.sub(
    r'        # 导出为 txt\n        try:\n            filepath = self\._export_to_txt\(\)\n            export_msg = f"\\n\\n📁 已导出为：{filepath}"\n        except Exception as e:\n            export_msg = f"\\n\\n⚠️ 导出失败：{e}"\n',
    '        export_msg = ""',
    content
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ writer_agent 已回归专业写作位置")
print("   移除: _handle_export_to, _handle_export, _build_export_operations, _extract_path, _get_project_title, _export_to_txt")
print("   保留: 所有写作核心方法")
