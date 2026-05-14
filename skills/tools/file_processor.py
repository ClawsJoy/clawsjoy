"""文件处理技能 - 支持多种格式"""

from skills.skill_interface import BaseSkill
import os
import json
from pathlib import Path
from datetime import datetime

class FileProcessorSkill(BaseSkill):
    name = "file_processor"
    description = "处理各种文件格式（PDF、Excel、Word、图片、文本）"
    version = "1.0.0"
    category = "utility"
    
    def __init__(self):
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, params):
        action = params.get("action", "read")
        file_path = params.get("file_path", "")
        
        if action == "read":
            return self.read_file(file_path)
        elif action == "list":
            return self.list_files()
        elif action == "delete_old":
            return self.delete_old_files()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def read_file(self, file_path):
        """读取文件内容"""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": "File not found"}
        
        ext = path.suffix.lower()
        
        try:
            if ext == '.txt':
                content = path.read_text(encoding='utf-8')
                return {"success": True, "content": content, "type": "text"}
            
            elif ext == '.json':
                with open(path, 'r') as f:
                    data = json.load(f)
                return {"success": True, "content": data, "type": "json"}
            
            elif ext == '.pdf':
                import PyPDF2
                content = []
                with open(path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content.append(page.extract_text())
                return {"success": True, "content": "\n".join(content), "type": "pdf", "pages": len(reader.pages)}
            
            elif ext in ['.xlsx', '.xls']:
                import pandas as pd
                df = pd.read_excel(path)
                return {"success": True, "content": df.to_dict(orient="records"), "type": "excel", "rows": len(df)}
            
            elif ext in ['.docx']:
                from docx import Document
                doc = Document(path)
                content = "\n".join([p.text for p in doc.paragraphs])
                return {"success": True, "content": content, "type": "word"}
            
            else:
                return {"success": False, "error": f"Unsupported file type: {ext}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_files(self):
        """列出上传的文件"""
        files = []
        for f in self.upload_dir.iterdir():
            if f.is_file():
                files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        return {"success": True, "files": files}
    
    def delete_old_files(self, hours=24):
        """删除旧文件"""
        import time
        now = time.time()
        deleted = 0
        for f in self.upload_dir.iterdir():
            if now - f.stat().st_mtime > hours * 3600:
                f.unlink()
                deleted += 1
        return {"success": True, "deleted": deleted}

skill = FileProcessorSkill()
