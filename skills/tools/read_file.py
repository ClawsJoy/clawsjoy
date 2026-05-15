"""
读取文件
"""
class Read_fileSkill:
    name = "read_file"
    description = "读取文件"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from pathlib import Path; path = params.get('path'); result = Path(path).read_text() if Path(path).exists() else None
        return {"success": True, "result": result}

skill = Read_fileSkill()
