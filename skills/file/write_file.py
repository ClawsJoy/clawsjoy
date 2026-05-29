"""写入文件"""
class WriteFileSkill:
    def execute(self, params):
        path = params.get('path', '')
        content = params.get('content', '')
        encoding = params.get('encoding', 'utf-8')
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return {"success": True, "message": f"已写入 {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
skill = WriteFileSkill()
