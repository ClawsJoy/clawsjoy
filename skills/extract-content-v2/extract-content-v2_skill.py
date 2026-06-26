"""内容提取"""
import re

class extract_content_v2:
    name = "extract-content-v2"
    description = "从文本提取结构化内容"
    version = "1.0.0"
    
    def execute(self, params):
        text = params.get("text", "")
        return {
            "success": True,
            "emails": re.findall(r'[\w.-]+@[\w.-]+\.\w+', text),
            "phones": re.findall(r'1[3-9]\d{9}', text),
            "urls": re.findall(r'https?://[^\s]+', text),
        }
