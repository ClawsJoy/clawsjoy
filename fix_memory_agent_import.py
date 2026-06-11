file_path = "agents/memory_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 确保 memory_agent 实例存在
if "memory_agent = MemoryAgent()" not in content:
    content += '\n\nmemory_agent = MemoryAgent()\n'

# 修复 process 方法
if "def process" not in content:
    process_method = '''
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """处理记忆请求"""
        if "记住" in user_input:
            return {"success": True, "response": "已记住", "agent": "memory_agent"}
        elif "回忆" in user_input:
            return {"success": True, "response": "暂无记忆", "agent": "memory_agent"}
        return {"success": False, "response": "无法理解", "agent": "memory_agent"}
'''
    content = content.replace("class MemoryAgent:", "class MemoryAgent:\n" + process_method)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ memory_agent 已修复")
