"""内容提取"""
import re
class extract_content:
    name = "extract-content"
    description = "文本内容提取"
    version = "1.0.0"
    def execute(self, params):
        text = params.get("text", "")
        return {"success": True, "emails": re.findall(r'[\w.-]+@[\w.-]+\.[\w.]+', text), "urls": re.findall(r'https?://[^\s]+', text)}
