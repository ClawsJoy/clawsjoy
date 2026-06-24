import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 找到 _save_state 方法并修改
old_save = '''    def _save_state(self):
        """保存创作状态到 memory"""
        if not self._session_id:
            return

        self._novel["updated_at"] = datetime.now().isoformat()
        self._novel["word_count"] = self._count_words()

        try:
            if self.memory:
                self.memory.add_session_memory(
                    self._session_id,
                    "writer_state",
                    {"novel_state": self._novel}
                )
        except Exception as e:
            print(f"[Writer] 保存状态失败: {e}")'''

new_save = '''    def _save_state(self):
        """保存创作状态到 memory - 只在有内容时保存"""
        if not self._session_id:
            return

        # 🔧 检查是否有内容：大纲或章节
        has_content = (
            self._novel.get("outline") or 
            self._novel.get("chapters") or
            self._novel.get("characters") or
            self._novel.get("status") != "idle"
        )
        
        if not has_content:
            print("[Writer] ⏭️ 跳过保存（无内容）")
            return

        self._novel["updated_at"] = datetime.now().isoformat()
        self._novel["word_count"] = self._count_words()

        try:
            if self.memory:
                self.memory.add_session_memory(
                    self._session_id,
                    "writer_state",
                    {"novel_state": self._novel}
                )
                print("[Writer] 💾 状态已保存")
        except Exception as e:
            print(f"[Writer] 保存状态失败: {e}")'''

content = content.replace(old_save, new_save)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ _save_state 已修复")
print("   - 只有在大纲/章节/角色/状态非 idle 时才保存")
print("   - 空状态不会覆盖已有数据")
