import re

file_path = "core/lib/chat_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# 确保 _llm_fallback 正确调用 LLM
old_llm_fallback = '''    def _llm_fallback(self, message: str, user_id: str, emotion, emotion_conf) -> Dict:
        """LLM兜底"""
        try:
            from core.lib.config import config

            resp = requests.post(
                f"{config.LLM_URL}/chat", json={"message": message}, timeout=60
            )'''

new_llm_fallback = '''    def _llm_fallback(self, message: str, user_id: str, emotion, emotion_conf) -> Dict:
        """LLM兜底 - 修复版"""
        try:
            import requests
            # 直接调用 LLM 服务
            resp = requests.post(
                "http://localhost:5012/chat", 
                json={"message": message}, 
                timeout=60,
                headers={"Content-Type": "application/json"}
            )'''

content = content.replace(old_llm_fallback, new_llm_fallback)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ chat_engine LLM 调用已修复")
