"""
列出文件
"""
class List_filesSkill:
    name = "list_files"
    description = "列出文件"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from pathlib import Path; directory = params.get('directory', '.'); result = [str(f) for f in Path(directory).iterdir() if f.is_file()]
        return {"success": True, "result": result}

skill = List_filesSkill()
