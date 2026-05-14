"""文档生成技能 - 让大脑能创建各种文档"""

from skills.skill_interface import BaseSkill
import requests

class DocGeneratorSkill(BaseSkill):
    name = "doc_generator"
    description = "创建文档（Word、Excel、PPT、Markdown）"
    version = "1.0.0"
    category = "content"
    
    def execute(self, params):
        doc_type = params.get("type", "md")
        title = params.get("title", "未命名")
        
        if doc_type == "docx":
            return self._create_docx(params)
        elif doc_type == "excel":
            return self._create_excel(params)
        elif doc_type == "ppt":
            return self._create_ppt(params)
        else:
            return self._create_md(params)
    
    def _create_docx(self, params):
        resp = requests.post("http://localhost:5007/docx", json={
            "title": params.get("title", "文档"),
            "content": params.get("content", "")
        })
        return resp.json()
    
    def _create_excel(self, params):
        resp = requests.post("http://localhost:5007/excel", json={
            "headers": params.get("headers", []),
            "rows": params.get("rows", []),
            "sheet_name": params.get("sheet_name", "Sheet1")
        })
        return resp.json()
    
    def _create_ppt(self, params):
        resp = requests.post("http://localhost:5007/ppt", json={
            "title": params.get("title", "演示文稿"),
            "slides": params.get("slides", [])
        })
        return resp.json()
    
    def _create_md(self, params):
        resp = requests.post("http://localhost:5007/md", json={
            "title": params.get("title", "文档"),
            "content": params.get("content", "")
        })
        return resp.json()

skill = DocGeneratorSkill()
