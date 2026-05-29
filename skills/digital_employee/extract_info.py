"""提取信息"""
class ExtractInfoSkill:
    def execute(self, params):
        text = params.get('text', '')
        # 简单提取
        import re
        emails = re.findall(r'\S+@\S+', text)
        phones = re.findall(r'1[3-9]\d{9}', text)
        return {"success": True, "emails": emails, "phones": phones}
skill = ExtractInfoSkill()
