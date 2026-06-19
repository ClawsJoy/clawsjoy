import re

file_path = "agents/code_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在路由条件中添加"名字"相关的路由
old_routes = '''        # 3.3 项目/文件操作
        if any(kw in t for kw in ["添加项目", "导入项目", "列出项目"]):
            return self._handle_project(user_input)

        if any(kw in t for kw in ["读取文件", "打开文件"]):
            return self._handle_file(user_input)

        # 3.4 默认：对话
        return self._handle_chat(user_input)'''

new_routes = '''        # 3.3 项目/文件操作
        if any(kw in t for kw in ["添加项目", "导入项目", "列出项目"]):
            return self._handle_project(user_input)

        if any(kw in t for kw in ["读取文件", "打开文件"]):
            return self._handle_file(user_input)

        # 3.4 记忆/名字查询
        if any(kw in t for kw in ["名字", "姓名", "叫什么", "我是谁"]):
            return self._handle_memory_query(user_input, context)

        # 3.5 默认：对话
        return self._handle_chat(user_input)'''

content = content.replace(old_routes, new_routes)

# 添加 _handle_memory_query 方法
memory_query_method = '''
    # ================================================================
    #  记忆查询（名字/身份）
    # ================================================================

    def _handle_memory_query(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理名字/身份查询，从记忆中获取"""
        try:
            # 从 context 中获取记忆
            memories = context.get("memories", []) if context else []
            
            # 在记忆中搜索名字
            for mem in memories:
                if isinstance(mem, dict):
                    content_text = mem.get("content", mem.get("user_input", ""))
                    if "名字" in content_text or "姓名" in content_text:
                        # 提取名字
                        import re
                        match = re.search(r'(?:名字|姓名)[：:]\s*(\\S+)', content_text)
                        if match:
                            name = match.group(1)
                            return self._resp(f"您的名字是：{name}")
                elif isinstance(mem, str):
                    if "名字" in mem or "姓名" in mem:
                        import re
                        match = re.search(r'(?:名字|姓名)[：:]\s*(\\S+)', mem)
                        if match:
                            name = match.group(1)
                            return self._resp(f"您的名字是：{name}")
            
            # 如果记忆中没有名字，调用 LLM 理解意图
            prompt = f"用户问：{user_input}\\n请判断用户是否在询问自己的名字，如果是，请礼貌地说明不知道；如果不是，请正常回复。"
            result = self._call_llm(prompt)
            return self._resp(result)
        except Exception as e:
            print(f"[CodeAgent] 记忆查询失败: {e}")
            return self._resp("我暂时无法获取您的名字信息。")
'''

# 在 _handle_chat 方法之前插入
content = content.replace(
    '    # ================================================================\n    #  默认：对话\n    # ================================================================\n\n    def _handle_chat(self, user_input: str) -> Dict:',
    memory_query_method + '\n    # ================================================================\n    #  默认：对话\n    # ================================================================\n\n    def _handle_chat(self, user_input: str) -> Dict:'
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ code_agent 已添加 _handle_memory_query 方法")
print("   用户问'我叫什么名字'时，会从记忆中查询")
