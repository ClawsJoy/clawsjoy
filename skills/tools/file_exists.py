"""
检查文件存在
"""
class File_existsSkill:
    name = "file_exists"
    description = "检查文件存在"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from pathlib import Path; path = params.get('path'); result = Path(path).exists()
        return {"success": True, "result": result}

skill = File_existsSkill()
