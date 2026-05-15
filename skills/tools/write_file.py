"""
写入文件
"""
class Write_fileSkill:
    name = "write_file"
    description = "写入文件"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from pathlib import Path; path = params.get('path'); content = params.get('content', ''); Path(path).write_text(content); result = f'写入成功: {path}'
        return {"success": True, "result": result}

skill = Write_fileSkill()
