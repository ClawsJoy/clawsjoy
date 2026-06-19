import re

file_path = "agents/code_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 semantic 访问：使用 getattr 安全访问
content = content.replace(
    'if self.semantic:',
    'if hasattr(self, "semantic") and self.semantic:'
)

content = content.replace(
    'if self.emotion:',
    'if hasattr(self, "emotion") and self.emotion:'
)

content = content.replace(
    'if self.reasoning and any(kw in t for kw in ["为什么", "怎么", "如何", "如果", "那么"]):',
    'if hasattr(self, "reasoning") and self.reasoning and any(kw in t for kw in ["为什么", "怎么", "如何", "如果", "那么"]):'
)

content = content.replace(
    'if self.knowledge:',
    'if hasattr(self, "knowledge") and self.knowledge:'
)

content = content.replace(
    'if self.task_decomposer and self._is_complex(user_input):',
    'if hasattr(self, "task_decomposer") and self.task_decomposer and self._is_complex(user_input):'
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ code_agent 已修复 - 使用 hasattr 安全访问属性")
